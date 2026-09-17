"""A deliberately small, local adapter for ``codex app-server --stdio``.

It is not an OAuth client: authentication remains entirely the responsibility of
the already installed Codex CLI.  The adapter only speaks JSON-RPC to that local
process and keeps each prompt in a fresh, isolated thread.
"""
import json
import os
import queue
import shutil
import subprocess
import tempfile
import threading
from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.runnables import Runnable


class CodexAppServerError(RuntimeError):
    """A safe diagnostic for a local Codex App Server failure."""


class CodexAppServer(Runnable):
    """Convert a LangChain prompt into one isolated Codex App Server turn."""

    def __init__(self, command: str = "codex", timeout: float = 60.0,
                 model: Optional[str] = None) -> None:
        if timeout <= 0:
            raise ValueError("Codex timeout must be greater than zero")
        self.command = command
        self.timeout = timeout
        self.model = model
        self._process: Optional[subprocess.Popen] = None
        self._tempdir: Optional[tempfile.TemporaryDirectory] = None
        self._closed = False
        self._initialized = False
        self._next_id = 0
        self._read_queue: "queue.Queue[object]" = queue.Queue()
        self._reader: Optional[threading.Thread] = None

    @staticmethod
    def available(command: str) -> bool:
        """Return whether the configured executable can be resolved locally."""
        return os.path.isabs(command) and os.access(command, os.X_OK) or bool(
            shutil.which(command)
        )

    def _id(self) -> int:
        self._next_id += 1
        return self._next_id

    def _start(self) -> None:
        if self._process is not None:
            return
        if self._closed:
            raise CodexAppServerError("Codex App Server is closed")
        if not self.available(self.command):
            raise CodexAppServerError(
                "Codex CLI is unavailable; install Codex and complete `codex login` "
                "on this trusted local machine."
            )
        self._tempdir = tempfile.TemporaryDirectory(prefix="airogue-codex-")
        try:
            self._process = subprocess.Popen(
                [self.command, "app-server", "--stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                cwd=self._tempdir.name,
            )
        except OSError as exc:
            self.close()
            raise CodexAppServerError(
                "Could not start Codex App Server; verify the local Codex installation."
            ) from exc
        self._reader = threading.Thread(target=self._read_stdout, daemon=True)
        self._reader.start()

    def _read_stdout(self) -> None:
        assert self._process is not None and self._process.stdout is not None
        try:
            for line in self._process.stdout:
                self._read_queue.put(line)
        finally:
            self._read_queue.put(None)

    def _send(self, payload: Dict[str, Any]) -> None:
        if self._process is None or self._process.stdin is None:
            raise CodexAppServerError("Codex App Server stdin is unavailable")
        try:
            self._process.stdin.write(json.dumps(payload) + "\n")
            self._process.stdin.flush()
        except (OSError, ValueError) as exc:
            raise CodexAppServerError("Codex App Server connection was lost") from exc

    def _receive(self) -> Dict[str, Any]:
        try:
            line = self._read_queue.get(timeout=self.timeout)
        except queue.Empty as exc:
            raise CodexAppServerError("Codex App Server timed out; try again or check Codex login.") from exc
        if line is None:
            code = self._process.poll() if self._process is not None else None
            raise CodexAppServerError(
                "Codex App Server exited before completing the request"
                + (" (non-zero exit)." if code else ".")
            )
        try:
            message = json.loads(str(line))
        except json.JSONDecodeError as exc:
            raise CodexAppServerError("Codex App Server returned malformed JSON-RPC output") from exc
        if not isinstance(message, dict):
            raise CodexAppServerError("Codex App Server returned an invalid JSON-RPC message")
        if "method" in message and "id" in message:
            # Never approve a tool or permission request.  Replying prevents a
            # compliant server from waiting indefinitely, then fail closed.
            self._send({"jsonrpc": "2.0", "id": message["id"], "error": {
                "code": -32000, "message": "AiRogue does not permit Codex tools or approvals"
            }})
            raise CodexAppServerError("Codex requested a tool or approval; the isolated backend refused it")
        return message

    def _request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        request_id = self._id()
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        while True:
            message = self._receive()
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise CodexAppServerError("Codex App Server rejected " + method + "; update Codex or check login.")
            if "result" not in message:
                raise CodexAppServerError("Codex App Server returned an invalid response")
            return message["result"]

    def _initialize(self) -> None:
        if self._initialized:
            return
        self._request("initialize", {"clientInfo": {"name": "airogue", "version": "0.1"}})
        self._send({"jsonrpc": "2.0", "method": "initialized", "params": {}})
        self._initialized = True

    @staticmethod
    def _prompt_text(input: Any) -> str:
        if hasattr(input, "to_messages"):
            messages = input.to_messages()
        elif isinstance(input, (list, tuple)):
            messages = input
        else:
            return str(input)
        parts = []
        for message in messages:
            if isinstance(message, BaseMessage):
                content = message.content
                parts.append(str(content))
            else:
                parts.append(str(message))
        return "\n\n".join(parts)

    @staticmethod
    def _assistant_text(params: Dict[str, Any]) -> Optional[str]:
        item = params.get("item", params)
        if not isinstance(item, dict):
            return None
        if item.get("type") not in ("agentMessage", "assistantMessage", "message"):
            return None
        if item.get("role") not in (None, "assistant"):
            return None
        text = item.get("text") or item.get("content")
        if isinstance(text, str):
            return text
        if isinstance(text, list):
            return "".join(part.get("text", "") for part in text if isinstance(part, dict))
        return None

    def invoke(self, input: Any, config: Optional[Dict[str, Any]] = None, **kwargs: Any) -> AIMessage:
        """Run one prompt.  Completion, not a text delta, is authoritative."""
        try:
            self._start()
            self._initialize()
            assert self._tempdir is not None
            cwd = self._tempdir.name
            thread = self._request("thread/start", {
                "cwd": cwd, "approvalPolicy": "never", "ephemeral": True,
            })
            thread_id = thread.get("thread", thread).get("id") if isinstance(thread, dict) else None
            if not thread_id:
                raise CodexAppServerError("Codex App Server did not return a thread id")
            sandbox = {"type": "readOnly", "access": {"type": "restricted",
                       "includePlatformDefaults": True, "readableRoots": [cwd]},
                       "networkAccess": False}
            params: Dict[str, Any] = {"threadId": thread_id, "input": [{"type": "text", "text": self._prompt_text(input)}],
                                      "cwd": cwd, "approvalPolicy": "never", "sandboxPolicy": sandbox}
            if self.model:
                params["model"] = self.model
            self._request("turn/start", params)
            final_text: Optional[str] = None
            while True:
                message = self._receive()
                if message.get("method") == "item/completed":
                    final_text = self._assistant_text(message.get("params", {})) or final_text
                if message.get("method") == "turn/completed":
                    turn = message.get("params", {}).get("turn", {})
                    if turn.get("status") not in (None, "completed"):
                        raise CodexAppServerError("Codex turn did not complete successfully")
                    if not final_text:
                        raise CodexAppServerError("Codex turn completed without a final assistant message")
                    return AIMessage(content=final_text)
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        """Idempotently stop the one process owned by this adapter."""
        if self._closed:
            return
        self._closed = True
        process, self._process = self._process, None
        if process is not None:
            if process.stdin is not None:
                try:
                    process.stdin.close()
                except OSError:
                    pass
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=2)
        if self._tempdir is not None:
            self._tempdir.cleanup()
            self._tempdir = None

    def __enter__(self) -> "CodexAppServer":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()
