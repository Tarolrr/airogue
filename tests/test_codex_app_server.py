"""Offline JSON-RPC tests for the local Codex adapter."""
import json
from unittest.mock import patch

import pytest
from langchain_core.messages import HumanMessage

from llm.providers.codex_app_server import CodexAppServer, CodexAppServerError


class _Input:
    def __init__(self):
        self.writes, self.closed = [], False
    def write(self, value): self.writes.append(value)
    def flush(self): pass
    def close(self): self.closed = True


class _Process:
    def __init__(self, messages):
        self.stdin = _Input()
        self.stdout = iter(json.dumps(message) + "\n" for message in messages)
        self.terminated = False
    def poll(self): return None
    def terminate(self): self.terminated = True
    def wait(self, timeout=None): return 0
    def kill(self): pass


def _messages():
    return [{"jsonrpc": "2.0", "id": 1, "result": {}},
            {"jsonrpc": "2.0", "id": 2, "result": {"thread": {"id": "thread-1"}}},
            {"jsonrpc": "2.0", "id": 3, "result": {}},
            {"jsonrpc": "2.0", "method": "item/completed", "params":
             {"item": {"type": "agentMessage", "text": "final answer"}}},
            {"jsonrpc": "2.0", "method": "turn/completed", "params":
             {"turn": {"status": "completed"}}}]


def test_protocol_waits_for_terminal_message_and_uses_isolated_policy():
    process = _Process(_messages())
    with patch("llm.providers.codex_app_server.subprocess.Popen", return_value=process), patch.object(CodexAppServer, "available", return_value=True):
        adapter = CodexAppServer(timeout=1)
        result = adapter.invoke([HumanMessage(content="hello")])
    assert result.content == "final answer"
    sent = [json.loads(line) for line in process.stdin.writes]
    assert [entry.get("method") for entry in sent[:4]] == ["initialize", "initialized", "thread/start", "turn/start"]
    thread, turn = sent[2]["params"], sent[3]["params"]
    assert thread["approvalPolicy"] == turn["approvalPolicy"] == "never"
    assert turn["cwd"] == thread["cwd"]
    assert turn["sandboxPolicy"]["access"]["readableRoots"] == [thread["cwd"]]
    assert turn["sandboxPolicy"]["networkAccess"] is False
    assert "writableRoots" not in turn["sandboxPolicy"]["access"]
    adapter.close()
    assert process.stdin.closed and process.terminated


def test_initialize_error_never_starts_a_thread_or_leaks_token(monkeypatch):
    process = _Process([{"jsonrpc": "2.0", "id": 1, "error": {"code": -1}}])
    monkeypatch.setenv("CODEX_ACCESS_TOKEN", "not-for-errors")
    with patch("llm.providers.codex_app_server.subprocess.Popen", return_value=process), patch.object(CodexAppServer, "available", return_value=True):
        with pytest.raises(CodexAppServerError) as exc_info:
            CodexAppServer(timeout=1).invoke("hello")
    assert "not-for-errors" not in str(exc_info.value)
    assert [json.loads(line).get("method") for line in process.stdin.writes] == ["initialize"]


def test_malformed_output_is_a_safe_transport_error():
    process = _Process([])
    process.stdout = iter(["not-json\n"])
    with patch("llm.providers.codex_app_server.subprocess.Popen", return_value=process), patch.object(CodexAppServer, "available", return_value=True):
        with pytest.raises(CodexAppServerError, match="malformed"):
            CodexAppServer(timeout=1).invoke("hello")
