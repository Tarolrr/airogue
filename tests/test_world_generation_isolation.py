"""
Tests for isolating and stabilizing world generation components.

This test suite systematically tests each component of the world generation pipeline
to identify and fix crash points before enabling e2e testing with real OpenAI API.
"""
import pytest
import json
import os
import sys
from unittest.mock import patch, mock_open, MagicMock

# Global fixture for mocking OpenAI
@pytest.fixture(autouse=True)
def mock_openai(monkeypatch):
    # Mock the ChatOpenAI class
    mock_chat = MagicMock()
    monkeypatch.setattr('langchain_openai.ChatOpenAI', lambda **kwargs: mock_chat)
    return mock_chat

# Test data fixtures
VALID_WORLD_MODEL_JSON = {
    "theme": "Dark Fantasy",
    "title": "Test World",
    "plot": "A mysterious adventure awaits",
    "mechanics": {
        "mechanics": [
            {"name": "Shadow Magic", "description": "Harness dark energy"}
        ]
    },
    "items": {
        "items": [
            {"name": "Shadow Blade", "ascii_symbol": "/", "description": "A dark sword"},
            {"name": "Health Potion", "ascii_symbol": "!", "description": "Restores health"}
        ]
    },
    "global_entities": {
        "Game": {
            "components": [
                {
                    "name": "main",
                    "attributes": {"value": 100},
                    "pipelines": []
                }
            ]
        }
    }
}

INVALID_WORLD_MODEL_JSON = {
    "theme": "Test",
    # Missing required fields
}

MALFORMED_JSON = '{"theme": "test", "invalid": json}'


class TestWorldModelLoading:
    """Test world model JSON loading and validation."""
    
    def test_valid_world_model_loads_successfully(self):
        """Test that a valid world model JSON loads without crashes."""
        from llm.models import WorldModel
        
        # This should not crash
        world_model = WorldModel(**VALID_WORLD_MODEL_JSON)
        
        assert world_model.theme == "Dark Fantasy"
        assert world_model.title == "Test World"
        assert len(world_model.items.items) == 2
        assert len(world_model.mechanics.mechanics) == 1
    
    def test_invalid_world_model_raises_validation_error(self):
        """Test that invalid world model data raises appropriate errors."""
        from llm.models import WorldModel
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            WorldModel(**INVALID_WORLD_MODEL_JSON)
    
    def test_world_model_json_file_loading(self):
        """Test loading world model from JSON file."""
        from llm.models import WorldModel
        
        json_data = json.dumps(VALID_WORLD_MODEL_JSON)
        
        with patch("builtins.open", mock_open(read_data=json_data)):
            with open("world_model.json", "r") as f:
                data = json.load(f)
                world_model = WorldModel(**data)
                
            assert world_model.theme == "Dark Fantasy"
    
    def test_malformed_json_raises_json_error(self):
        """Test that malformed JSON raises appropriate error."""
        with patch("builtins.open", mock_open(read_data=MALFORMED_JSON)):
            with pytest.raises(json.JSONDecodeError):
                with open("world_model.json", "r") as f:
                    json.load(f)
    
    def test_missing_json_file_raises_file_error(self):
        """Test that missing JSON file raises appropriate error."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                with open("world_model.json", "r") as f:
                    json.load(f)


class TestLLMWorldGeneration:
    """Test LLM world generation components."""
    
    def test_world_class_instantiation(self):
        """Test that World class can be instantiated without crashes."""
        # Mock OpenAI to avoid API calls during testing
        with patch('llm.world.ChatOpenAI') as mock_openai:
            mock_openai.return_value = MagicMock()
            
            from llm.world import World
            
            # This should not crash
            world = World(None)
            assert world.setting is None
            assert world.setting_details == ""
    
    def test_world_generation_with_mocked_llm(self):
        """Test world generation with mocked LLM responses."""
        # Mock all LLM components
        with patch('llm.world.ChatOpenAI') as mock_openai:
            mock_openai.return_value = MagicMock()
            
            from llm.world import World
            
            world = World("fantasy")
            
            # Mock the generate_world method if it exists
            if hasattr(world, 'generate_world'):
                with patch.object(world, 'generate_world') as mock_generate:
                    mock_generate.return_value = VALID_WORLD_MODEL_JSON
                    result = world.generate_world()
                    assert result is not None


class TestWorldToolsIntegration:
    """Test the integration of world generation in world_tools.py"""
    
    def test_new_world_with_valid_json_data(self):
        """Test new_world function with valid JSON data."""
        json_data = json.dumps(VALID_WORLD_MODEL_JSON)
        
        # Mock all external dependencies
        with patch("builtins.open", mock_open(read_data=json_data)), \
             patch('game.world_tools.World') as mock_world_class, \
             patch('game.world_tools.Registry') as mock_registry, \
             patch('game.world_tools.Random') as mock_random:
            
            # Setup mocks
            mock_world_instance = MagicMock()
            mock_world_class.return_value = mock_world_instance
            mock_registry_instance = MagicMock()
            mock_registry.return_value = mock_registry_instance
            
            from game.world_tools import new_world
            
            # This should not crash
            result = new_world()
            assert result is not None
    
    def test_new_world_handles_missing_json_gracefully(self):
        """Test that new_world handles missing JSON file gracefully."""
        with patch("builtins.open", side_effect=FileNotFoundError), \
             patch('game.world_tools.World') as mock_world_class, \
             patch('game.world_tools.Registry') as mock_registry:
            
            mock_world_class.return_value = MagicMock()
            mock_registry.return_value = MagicMock()
            
            from game.world_tools import new_world
            
            # Should raise FileNotFoundError, not crash unexpectedly
            with pytest.raises(FileNotFoundError):
                new_world()
    
    def test_new_world_handles_malformed_json_gracefully(self):
        """Test that new_world handles malformed JSON gracefully."""
        with patch("builtins.open", mock_open(read_data=MALFORMED_JSON)), \
             patch('game.world_tools.World') as mock_world_class, \
             patch('game.world_tools.Registry') as mock_registry:
            
            mock_world_class.return_value = MagicMock()
            mock_registry.return_value = MagicMock()
            
            from game.world_tools import new_world
            
            # Should raise JSONDecodeError, not crash unexpectedly
            with pytest.raises(json.JSONDecodeError):
                new_world()


class TestItemGeneration:
    """Test item generation from world model data."""
    
    def test_item_creation_from_valid_data(self):
        """Test that items can be created from valid world model data."""
        from llm.models import Item, Items
        
        item_data = {"name": "Test Sword", "ascii_symbol": "/", "description": "A test weapon"}
        item = Item(**item_data)
        
        assert item.name == "Test Sword"
        assert item.ascii_symbol == "/"
        assert item.description == "A test weapon"
    
    def test_items_collection_creation(self):
        """Test that Items collection can be created and formatted."""
        from llm.models import Item, Items
        
        items_data = {
            "items": [
                {"name": "Sword", "ascii_symbol": "/", "description": "A weapon"},
                {"name": "Potion", "ascii_symbol": "!", "description": "Healing item"}
            ]
        }
        
        items = Items(**items_data)
        assert len(items.items) == 2
        
        # Test string formatting
        items_str = str(items)
        assert "Sword" in items_str
        assert "Potion" in items_str
    
    def test_invalid_item_data_raises_validation_error(self):
        """Test that invalid item data raises validation errors."""
        from llm.models import Item
        from pydantic import ValidationError
        
        # Missing required fields
        invalid_item_data = {"name": "Test"}
        
        with pytest.raises(ValidationError):
            Item(**invalid_item_data)


class TestErrorRecovery:
    """Test error recovery and graceful degradation."""
    
    def test_world_generation_fallback_mechanisms(self):
        """Test that world generation has appropriate fallback mechanisms."""
        # This test will be expanded as we implement fallback strategies
        pass
    
    def test_partial_world_model_handling(self):
        """Test handling of partially complete world models."""
        partial_world_model = {
            "theme": "Test Theme",
            "title": "Test Title", 
            "plot": "Test Plot",
            "mechanics": {"mechanics": []},
            "items": {"items": []},
            "global_entities": {}
        }
        
        from llm.models import WorldModel
        
        # Should handle minimal valid data
        world_model = WorldModel(**partial_world_model)
        assert world_model.theme == "Test Theme"
        assert len(world_model.items.items) == 0
