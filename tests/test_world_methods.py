"""
Tests for the World class methods in llm/world.py.
Covers the content generation methods to ensure they work correctly
with the new modular structure that delegates to WorldGenerator.
"""
import pytest
from unittest.mock import patch, MagicMock
import json
import os

from llm.models import Theme, WorldModel, Items, GameMechanics

@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    mock = MagicMock()
    mock.invoke.return_value = "Mocked LLM response"
    return mock

@pytest.fixture
def mock_theme_parser():
    """Create a mock theme parser that returns predefined themes."""
    mock = MagicMock()
    mock.get_format_instructions.return_value = "Theme format instructions"
    mock.invoke.return_value = mock.parse.return_value = {
        "themes": [
            "Dark Fantasy", 
            "Cyberpunk", 
            "Space Opera", 
            "Post-Apocalyptic", 
            "Steampunk",
            "Medieval", 
            "Horror", 
            "Pirate Adventure", 
            "Wild West", 
            "Mythological"
        ]
    }
    return mock

@pytest.fixture
def mock_item_parser():
    """Create a mock item parser that returns predefined items."""
    mock = MagicMock()
    mock.get_format_instructions.return_value = "Item format instructions"
    mock.invoke.return_value = mock.parse.return_value = {
        "items": [
            {
                "name": "Magic Sword",
                "ascii_symbol": "/",
                "description": "A powerful enchanted blade"
            },
            {
                "name": "Health Potion",
                "ascii_symbol": "!",
                "description": "Restores health when consumed"
            }
        ]
    }
    return mock

@pytest.fixture
def mock_gm_parser():
    """Create a mock game mechanics parser that returns predefined mechanics."""
    mock = MagicMock()
    mock.get_format_instructions.return_value = "Game mechanics format instructions"
    mock.invoke.return_value = mock.parse.return_value = {
        "mechanics": [
            {
                "name": "Shadow Magic",
                "description": "Harness dark energy for special attacks"
            },
            {
                "name": "Resource Management",
                "description": "Carefully manage limited supplies"
            }
        ]
    }
    return mock

class TestWorldMethods:
    """Tests for World class methods."""
    
    def test_theme_generation(self):
        """Test theme() method returns themes correctly."""
        with patch('llm.generators.base.ChatOpenAI') as mock_chat:
            
            # Setup mocks
            mock_chat.return_value = MagicMock()
            
            # Import inside test to use mocks
            from llm.world import World
            world = World(None)
            
            # Mock the generator's generate_themes method
            world.generator.generate_themes = MagicMock()
            world.generator.generate_themes.return_value = {"themes": ["Theme1", "Theme2", "Theme3", "Theme4", "Theme5", "Theme6", "Theme7", "Theme8", "Theme9", "Theme10"]}
            
            # Call the method
            result = world.theme()
            
            # Verify the result - World.theme() returns the first theme as a string
            assert result == "Theme1"
            
            # Verify the generator method was called
            world.generator.generate_themes.assert_called_once()
    
    def test_generate_title(self):
        """Test generate_title() method returns a title based on theme."""
        with patch('llm.generators.base.ChatOpenAI') as mock_chat:
            # Setup mocks
            mock_chat.return_value = MagicMock()
            
            # Import inside test to use mocks
            from llm.world import World
            world = World(None)
            
            # Mock the generator's generate_title method
            world.generator.generate_title = MagicMock()
            world.generator.generate_title.return_value = "Dark Fantasy Title"
            
            # Call the method
            result = world.generate_title("Dark Fantasy")
            
            # Verify the result
            assert isinstance(result, str)
            assert result == "Dark Fantasy Title"
            
            # Verify the generator method was called with the theme
            world.generator.generate_title.assert_called_once_with("Dark Fantasy")
            
    def test_generate_plot(self):
        """Test generate_plot() method returns a plot based on theme and title."""
        with patch('llm.generators.base.ChatOpenAI') as mock_chat:
            # Setup mocks
            mock_chat.return_value = MagicMock()
            
            # Import inside test to use mocks
            from llm.world import World
            world = World(None)
            
            # Mock the generator's generate_plot method
            world.generator.generate_plot = MagicMock()
            world.generator.generate_plot.return_value = "This is a test plot for a dark fantasy game."
            
            # Call the method
            result = world.generate_plot("Dark Fantasy", "Shadow Realm")
            
            # Verify the result
            assert isinstance(result, str)
            assert result == "This is a test plot for a dark fantasy game."
            
            # Verify the generator method was called with both theme and title
            world.generator.generate_plot.assert_called_once_with("Dark Fantasy", "Shadow Realm")
            
    def test_generate_items(self):
        """Test generate_items() method returns items based on mechanics."""
        with patch('llm.generators.base.ChatOpenAI') as mock_chat:
            
            # Setup mocks
            mock_chat.return_value = MagicMock()
            
            # Import inside test to use mocks
            from llm.world import World
            world = World(None)
            
            # Setup test data
            test_mechanic = GameMechanics(mechanics=[
                {"name": "Combat", "description": "Fighting monsters"}
            ])
            
            # Mock the generator's generate_items method
            world.generator.generate_items = MagicMock()
            test_items = [
                {"name": "Sword", "ascii_symbol": "/", "description": "A weapon"},
                {"name": "Shield", "ascii_symbol": "O", "description": "For defense"}
            ]
            world.generator.generate_items.return_value = test_items
            
            # Call the method
            result = world.generate_items(test_mechanic)
            
            # Verify the result
            assert isinstance(result, list)
            assert len(result) == 2
            assert isinstance(result[0], dict)
            assert 'name' in result[0]
            assert result[0]['name'] == "Sword"
            assert result[1]['name'] == "Shield"
            
            # Verify the generator method was called with the game mechanic
            world.generator.generate_items.assert_called_once_with(test_mechanic)
    
    def test_generate_world_integration(self):
        """Test generate_world() method creates a complete world model."""
        with patch('llm.generators.base.ChatOpenAI') as mock_chat:
            # Setup mocks
            mock_chat.return_value = MagicMock()
            
            # Import inside test to use mocks
            from llm.world import World
            
            # Create a sample world model for the mock return
            test_world_model = WorldModel(
                theme="Dark Fantasy",
                title="Shadow Realm",
                plot="A dark adventure awaits.",
                mechanics=GameMechanics(mechanics=[
                    {"name": "Combat", "description": "Fighting monsters"}
                ]),
                items=Items(items=[
                    {"name": "Sword", "ascii_symbol": "/", "description": "A weapon"}
                ]),
                global_entities={
                    "player": {"entity_id": "player", "name": "Player", "x": 0, "y": 0}
                }
            )
            
            # Create world instance and mock generator method
            world = World(None)
            world.generator.generate = MagicMock(return_value=test_world_model)
            
            # Call the method
            result = world.generate_world()
            
            # Verify the result is a complete WorldModel
            assert isinstance(result, WorldModel)
            assert result.theme == "Dark Fantasy"
            assert result.title == "Shadow Realm"
            assert result.plot == "A dark adventure awaits."
            assert len(result.mechanics.mechanics) > 0
            assert len(result.items.items) > 0
            assert "player" in result.global_entities
            
            # Verify the generator method was called
            world.generator.generate.assert_called_once()
