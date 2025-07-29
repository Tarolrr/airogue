"""A collection of game states."""
from __future__ import annotations

from typing import Final

import attrs
import tcod.console
import tcod.event
from tcod.event import KeySym

import g
from game.components import Gold, Graphic, Position, Name, Description
from game.tags import IsItem, IsPlayer, OnMap

DIRECTION_KEYS: Final = {
    # Arrow keys
    KeySym.LEFT: (-1, 0),
    KeySym.RIGHT: (1, 0),
    KeySym.UP: (0, -1),
    KeySym.DOWN: (0, 1),
    # Arrow key diagonals
    KeySym.HOME: (-1, -1),
    KeySym.END: (-1, 1),
    KeySym.PAGEUP: (1, -1),
    KeySym.PAGEDOWN: (1, 1),
    # Keypad
    KeySym.KP_4: (-1, 0),
    KeySym.KP_6: (1, 0),
    KeySym.KP_8: (0, -1),
    KeySym.KP_2: (0, 1),
    KeySym.KP_7: (-1, -1),
    KeySym.KP_1: (-1, 1),
    KeySym.KP_9: (1, -1),
    KeySym.KP_3: (1, 1),
    # VI keys
    KeySym.h: (-1, 0),
    KeySym.l: (1, 0),
    KeySym.k: (0, -1),
    KeySym.j: (0, 1),
    KeySym.y: (-1, -1),
    KeySym.b: (-1, 1),
    KeySym.u: (1, -1),
    KeySym.n: (1, 1),
}


@attrs.define(eq=False)
class InGame:
    """Primary in-game state."""

    def on_event(self, event: tcod.event.Event) -> None:
        """Handle events for the in-game state."""
        (player,) = g.world.Q.all_of(tags=[IsPlayer])
        (game_component,) = g.world.Q.all_of(components=[])  # TODO fix
        match event:
            case tcod.event.Quit():
                raise SystemExit()
            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:
                game_component.attributes["time"] += 1
                game_component.signals["tick"].emit(game_component.attributes["time"])
                # tcod.event
                player.components[Position] += DIRECTION_KEYS[sym]
                # Auto pickup gold
                found = False
                for gold in g.world.Q.all_of(tags=[player.components[Position], IsItem, OnMap]):
                    # player.components[Gold] += gold.components[Gold]
                    text = f"Standing on {gold.components[Name]}: {gold.components[Description]}"
                    g.world[None].components[("Text", str)] = text
                    found = True
                
                if not found:
                    g.world[None].components[("Text", str)] = ""
            case tcod.event.KeyDown(sym=sym) if sym == KeySym.l:
                game_component.signals["key_pressed"].emit("action_1")
            case tcod.event.KeyDown(sym=sym) if sym == KeySym.k:
                game_component.signals["key_pressed"].emit("action_2")
    def on_draw(self, console: tcod.console.Console) -> None:
        """Draw the standard screen."""
        for entity in g.world.Q.all_of(components=[Position, Graphic], tags=[OnMap]):
            pos = entity.components[Position]
            if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
                continue
            graphic = entity.components[Graphic]
            console.rgb[["ch", "fg"]][pos.y, pos.x] = graphic.ch, graphic.fg

        if text := g.world[None].components.get(("Text", str)):
            console.print_box(x=0, y=console.height - 5, width=console.width, height=5, string=text, fg=(255, 255, 255), bg=(0, 0, 0))

