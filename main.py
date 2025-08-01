#!/usr/bin/env python3
"""Main entry-point module. This script is used to start the program."""
from __future__ import annotations

import tcod.console
import tcod.context
import tcod.event
import tcod.tileset

import g
import game.states
import game.world_tools


def main() -> None:
    """Entry point function."""
    tileset = tcod.tileset.load_tilesheet(
        "data/Alloy_curses_12x12.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
    )
    tcod.tileset.procedural_block_elements(tileset=tileset)
    console = tcod.console.Console(80, 50)
    state = game.states.InGame()
    g.world = game.world_tools.new_world()
    with tcod.context.new(console=console, tileset=tileset) as g.context:
        while True:  # Main loop
            console.clear()  # Clear the console before any drawing
            state.on_draw(console)  # Draw the current state
            g.context.present(console)  # Render the console to the window and show it
            for event in tcod.event.wait():  # Event loop, blocks until pending events exist
                print(event)
                state.on_event(event)  # Dispatch events to the state


if __name__ == "__main__":
    import json

    # # Read the original world_model.json file
    # with open('world_model.json', 'r') as file:
    #     world_model_data = json.load(file)

    # # Write the formatted data to a new file
    # with open('formatted_world_model.json', 'w') as formatted_file:
    #     json.dump(world_model_data, formatted_file, indent=4)
    # def test_print(x):
        # print(x)
        # return {}

    # from langchain_core.runnables import RunnableLambda
    # from langchain_core.runnables.passthrough import identity
    # run = {"test": identity} | RunnableLambda(test_print)
    # run.invoke(None)
    # exit()
    main()
