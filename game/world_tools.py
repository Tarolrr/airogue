"""Functions for working with worlds."""
from __future__ import annotations
import json
from random import Random, choice

from tcod.ecs import Registry

from game.components import Gold, Graphic, Position, Name, Description
from game.tags import IsActor, IsItem, IsPlayer, OnMap
from llm.world import World, WorldModel
from slots import set_value, change_value, end_game


def new_world() -> Registry:
    """Return a freshly generated world."""
    world = Registry()

    rng = world[None].components[Random] = Random()

    player = world[object()]
    player.components[Position] = Position(5, 5)
    player.components[Graphic] = Graphic(ord("@"))
    player.components[Gold] = 0
    player.tags |= {IsPlayer, IsActor}


    llmworld = World(None)
    # world_model = llmworld.generate_world()
    with open("world_model.json", "r") as f:
        world_model = WorldModel(**json.load(f))

    game_entity = world["Game"]
    game_entity.components["main"] = world_model.global_entities["Game"].components[0]
    game_entity.components["main"].signals["game_start"].emit()
    game_entity.components["main"].slots["set_value"] = set_value
    game_entity.components["main"].slots["change_value"] = change_value
    game_entity.components["main"].slots["end_game"] = end_game

    for ent in world_model.global_entities:
        if ent.name == "Game":
            continue
        entity = world[ent.name]
        # entity.components = ent.components
        for comp in ent.components:
            entity.components[comp.name] = comp
        # entity.tags = {IsActor}
    world_model.print()
    # for _ in range(10):
    #     gold = world[object()]
    #     gold.components[Position] = Position(rng.randint(0, 20), rng.randint(0, 20))
    #     gold.components[Graphic] = Graphic(ord("$"), fg=(255, 255, 0))
    #     gold.components[Gold] = rng.randint(1, 10)
    #     gold.tags |= {IsItem}

    for _ in range(20):
        item_model = choice(world_model.items.items)
        item = world[object()]
        item.components[Position] = Position(rng.randint(0, 20), rng.randint(0, 20))
        item.components[Graphic] = Graphic(ord(item_model.ascii_symbol), fg=(255, 255, 0))
        item.components[Name] = item_model.name
        item.components[Description] = item_model.description
        item.tags |= {IsItem, OnMap}

    return world
