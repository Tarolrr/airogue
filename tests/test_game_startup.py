"""Smoke tests for the real game loop without a graphical display or LLM."""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
import tcod.console
import tcod.ecs
import tcod.event

import g
import main
from game.components import Graphic, Position
from game.states import InGame
from game.tags import IsPlayer, OnMap


class RecordingContext:
    """Offscreen context double which observes context-manager cleanup."""

    def __init__(self, console: tcod.console.Console, *, present_error: Exception | None = None) -> None:
        self.console = console
        self.present_error = present_error
        self.entered = False
        self.exited = False
        self.presented = False

    def __enter__(self) -> RecordingContext:
        self.entered = True
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        self.exited = True
        return False

    def present(self, console: tcod.console.Console) -> None:
        self.presented = True
        assert console is self.console
        assert console.rgb["ch"][9, 7] == ord("X")
        if self.present_error is not None:
            raise self.present_error


@pytest.fixture
def game_world() -> tcod.ecs.Registry:
    """Return a minimal real registry; world loading is intentionally excluded."""
    world = tcod.ecs.Registry()
    player = world["player"]
    player.components[Position] = Position(0, 0)
    player.tags.add(IsPlayer)

    visible = world["visible"]
    visible.components[Position] = Position(7, 9)
    visible.components[Graphic] = Graphic(ord("X"))
    visible.tags.add(OnMap)
    return world


@pytest.fixture(autouse=True)
def restore_globals() -> Iterator[None]:
    """Do not leak mutable application state into other tests."""
    old_world = getattr(g, "world", None)
    old_context = getattr(g, "context", None)
    had_world = hasattr(g, "world")
    had_context = hasattr(g, "context")
    yield
    if had_world:
        g.world = old_world
    elif hasattr(g, "world"):
        del g.world
    if had_context:
        g.context = old_context
    elif hasattr(g, "context"):
        del g.context


def test_main_draws_a_frame_and_releases_context_on_quit(monkeypatch, game_world) -> None:
    """The production entry point draws, dispatches Quit, and cleans up."""
    console = tcod.console.Console(80, 50)
    context = RecordingContext(console)
    calls = 0

    def new_world() -> tcod.ecs.Registry:
        nonlocal calls
        calls += 1
        return game_world

    monkeypatch.setattr(main.game.world_tools, "new_world", new_world)
    monkeypatch.setattr(main.tcod.console, "Console", lambda width, height: console)
    monkeypatch.setattr(main.tcod.tileset, "load_tilesheet", lambda *args, **kwargs: object())
    monkeypatch.setattr(main.tcod.tileset, "procedural_block_elements", lambda **kwargs: None)
    monkeypatch.setattr(main.tcod.context, "new", lambda **kwargs: context)
    event_batches = iter(((tcod.event.Quit(),),))

    def wait() -> Iterator[tcod.event.Event]:
        try:
            return iter(next(event_batches))
        except StopIteration as error:
            raise AssertionError("event queue unexpectedly exhausted") from error

    monkeypatch.setattr(main.tcod.event, "wait", wait)

    with pytest.raises(SystemExit):
        main.main()

    assert calls == 1
    assert context.entered
    assert context.presented
    assert context.exited
    assert g.world is game_world


def test_main_releases_context_when_present_fails(monkeypatch, game_world) -> None:
    """Rendering failures propagate but still execute the context cleanup."""
    console = tcod.console.Console(80, 50)
    error = RuntimeError("present failed")
    context = RecordingContext(console, present_error=error)
    monkeypatch.setattr(main.game.world_tools, "new_world", lambda: game_world)
    monkeypatch.setattr(main.tcod.console, "Console", lambda width, height: console)
    monkeypatch.setattr(main.tcod.tileset, "load_tilesheet", lambda *args, **kwargs: object())
    monkeypatch.setattr(main.tcod.tileset, "procedural_block_elements", lambda **kwargs: None)
    monkeypatch.setattr(main.tcod.context, "new", lambda **kwargs: context)

    with pytest.raises(RuntimeError, match="present failed"):
        main.main()

    assert context.exited


def test_quit_does_not_query_an_incomplete_registry(game_world) -> None:
    """Quit remains reliable even if the registry has multiple entities."""
    game_world["another entity"]
    g.world = game_world

    with pytest.raises(SystemExit):
        InGame().on_event(tcod.event.Quit())
