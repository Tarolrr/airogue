"""Predefined slots. All the ganerated slots should ultimately use these."""
from tags import OnMap
import g
from components import Position


def end_game():
    raise Exception("Game is over.")


def change_value(component, attribute, value):
    g.world[component].attributes[attribute] += value


def set_value(component, attribute, value):
    g.world[component].attributes[attribute] = value


def remove_from_map(query):
    # for entity in g.world.Q.all_of(tags=query):
    # g.world[entity].tags.remove(OnMap)
    pass

def add_to_map(entity):
    g.world[entity].tags.add(OnMap)


def move_entity(entity, x, y):
    g.world[entity].components[Position].x = x
    g.world[entity].components[Position].y = y

def add_to_list(entity_to_add, entity, component, attribute):
    g.world[entity].components[component].attributes[attribute].append(entity_to_add)
