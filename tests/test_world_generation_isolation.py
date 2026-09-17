"""Model validation and isolated tests for the ``World`` compatibility wrapper."""
import json
from unittest.mock import MagicMock, patch

import pytest


VALID_WORLD_MODEL_JSON = {
    "theme": "Dark Fantasy",
    "title": "Test World",
    "plot": "A mysterious adventure awaits",
    "mechanics": {"mechanics": [{"name": "Shadow Magic", "description": "Harness dark energy"}]},
    "items": {"items": [{"name": "Shadow Blade", "ascii_symbol": "/", "description": "A dark sword"}]},
    "global_entities": {},
}


class TestWorldModelLoading:
    def test_valid_world_model_loads_successfully(self):
        from llm.models import WorldModel

        world_model = WorldModel(**VALID_WORLD_MODEL_JSON)

        assert world_model.theme == "Dark Fantasy"
        assert world_model.items.items[0].ascii_symbol == "/"
        assert world_model.mechanics.mechanics[0].name == "Shadow Magic"

    def test_invalid_world_model_raises_validation_error(self):
        from llm.models import WorldModel
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            WorldModel(theme="Test")

    def test_malformed_json_raises_json_error(self):
        with pytest.raises(json.JSONDecodeError):
            json.loads('{"theme": "test", "invalid": json}')


class TestLLMWorldGeneration:
    def test_world_initialization_delegates_to_world_generator(self):
        with patch("llm.world.WorldGenerator") as world_generator:
            from llm.world import World

            generator = MagicMock()
            generator.llm = MagicMock()
            world_generator.return_value = generator

            world = World("fantasy", api_key="test-key")

        assert world.setting == "fantasy"
        assert world.setting_details == ""
        world_generator.assert_called_once_with(api_key="test-key")

    def test_world_generation_delegates_to_generator(self):
        with patch("llm.world.WorldGenerator") as world_generator:
            from llm.world import World

            generator = MagicMock()
            generator.llm = MagicMock()
            generator.generate.return_value = VALID_WORLD_MODEL_JSON
            world_generator.return_value = generator

            world = World(None)
            result = world.generate_world()

        assert result == VALID_WORLD_MODEL_JSON
        generator.generate.assert_called_once_with()


class TestItemGeneration:
    def test_items_collection_creation(self):
        from llm.models import Items

        items = Items(**VALID_WORLD_MODEL_JSON["items"])

        assert str(items) == "- [/] Shadow Blade: A dark sword"

    def test_invalid_item_data_raises_validation_error(self):
        from llm.models import Item
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Item(name="Test")
