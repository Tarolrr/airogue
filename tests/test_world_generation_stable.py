"""
Focused tests for world generation that properly use mocks to avoid API dependencies.

This test suite uses the existing test fixtures from conftest.py to properly mock
OpenAI dependencies and test just the world generation logic.
"""
import pytest
import json
import os
from unittest.mock import patch, mock_open, MagicMock

# Test data for isolated world model tests
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


class TestWorldModelStability:
    """Test world model validation using our existing fixtures."""
    
    def test_world_model_validation(self, sample_theme, sample_plot, mock_llm):
        """Test that WorldModel can be created from our test fixtures."""
        from llm.models import WorldModel, Items, GameMechanics
        
        # Create basic world model from our fixtures
        items = Items(items=[{
            "name": "Test Item",
            "ascii_symbol": "!",
            "description": "Test description"
        }])
        
        mechanics = GameMechanics(mechanics=[{
            "name": "Test Mechanic",
            "description": "Test mechanic description"
        }])
        
        # Create a valid world model
        world_model = WorldModel(
            theme=sample_theme.name,
            title="Test World",
            plot=sample_plot.summary,
            mechanics=mechanics,
            items=items,
            global_entities={}
        )
        
        # Verify basic fields
        assert world_model.theme == sample_theme.name
        assert world_model.title == "Test World"
        assert len(world_model.items.items) == 1


class TestWorldToolsWithMocks:
    """Test world_tools.py with proper mocking."""
    
    @patch('game.world_tools.Registry')
    @patch('game.world_tools.Random')
    def test_new_world_function_returns_registry(self, mock_random, mock_registry, mock_llm):
        """Test that new_world() function returns a registry."""
        # Setup mocks
        mock_registry_instance = MagicMock()
        mock_registry.return_value = mock_registry_instance
        mock_random_instance = MagicMock()
        mock_random.return_value = mock_random_instance
        
        # Create a patch for the World class
        with patch('game.world_tools.World') as mock_world_class, \
             patch('builtins.open', mock_open(read_data=json.dumps(VALID_WORLD_MODEL_JSON))):
            
            # Create mock World instance
            mock_world_instance = MagicMock()
            mock_world_class.return_value = mock_world_instance
            
            # Now we can safely import and test
            from game.world_tools import new_world
            
            # Test function
            result = new_world()
            
            # Verify result
            assert result is not None
            assert result == mock_registry_instance  # Should return the registry instance
    
    @patch('game.world_tools.Registry')
    @patch('game.world_tools.Random')
    def test_new_world_handles_json_errors_gracefully(self, mock_random, mock_registry):
        """Test that new_world handles JSON errors properly."""
        # Setup mocks
        mock_registry_instance = MagicMock()
        mock_registry.return_value = mock_registry_instance
        
        # Create a patch for builtins.open to simulate a file not found error
        with patch('game.world_tools.World') as mock_world_class, \
             patch('builtins.open', side_effect=FileNotFoundError):
            
            # Create mock World instance
            mock_world_instance = MagicMock()
            mock_world_class.return_value = mock_world_instance
            
            # Import the function
            from game.world_tools import new_world
            
            # Test that it raises appropriate error
            with pytest.raises(FileNotFoundError):
                new_world()
