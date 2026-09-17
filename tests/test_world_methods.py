"""Observable delegation tests for the legacy ``World`` wrapper."""
from unittest.mock import MagicMock, patch

import pytest

from llm.models import GameMechanics, Items, WorldModel


@pytest.fixture
def world_and_generator():
    with patch("llm.world.WorldGenerator") as world_generator:
        from llm.world import World

        generator = MagicMock()
        generator.llm = MagicMock()
        world_generator.return_value = generator
        yield World(None), generator


def test_theme_returns_first_generated_theme(world_and_generator):
    world, generator = world_and_generator
    generator.generate_themes.return_value = {"themes": ["Theme 1", "Theme 2"]}

    assert world.theme() == "Theme 1"
    generator.generate_themes.assert_called_once_with()


def test_generate_title_delegates_and_records_design_doc(world_and_generator):
    world, generator = world_and_generator
    generator.generate_title.return_value = "Shadow Realm"

    assert world.generate_title("Dark Fantasy") == "Shadow Realm"
    generator.generate_title.assert_called_once_with("Dark Fantasy")
    assert world.design_doc == "Theme: Dark Fantasy\nTitle: Shadow Realm\n"


def test_generate_plot_delegates_and_records_design_doc(world_and_generator):
    world, generator = world_and_generator
    generator.generate_plot.return_value = "Find the artifact."

    assert world.generate_plot("Dark Fantasy", "Shadow Realm") == "Find the artifact."
    generator.generate_plot.assert_called_once_with("Dark Fantasy", "Shadow Realm")
    assert world.design_doc == "Plot: Find the artifact.\n"


def test_generate_items_wraps_single_mechanic_mapping(world_and_generator):
    world, generator = world_and_generator
    mechanic = {"name": "Combat", "description": "Fight monsters"}
    generator.generate_items.return_value = [{"name": "Sword", "ascii_symbol": "/", "description": "A weapon"}]

    assert world.generate_items(mechanic)[0]["name"] == "Sword"
    generator.generate_items.assert_called_once_with(GameMechanics(mechanics=[mechanic]))


def test_generate_world_delegates_complete_model(world_and_generator):
    world, generator = world_and_generator
    model = WorldModel(
        theme="Dark Fantasy",
        title="Shadow Realm",
        plot="Find the artifact.",
        mechanics=GameMechanics(mechanics=[]),
        items=Items(items=[]),
    )
    generator.generate.return_value = model

    assert world.generate_world() is model
    generator.generate.assert_called_once_with()
