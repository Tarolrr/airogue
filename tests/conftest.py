"""
Pytest configuration and shared fixtures for AiRogue tests.
"""
import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

# Test data fixtures
@pytest.fixture
def sample_generation_context():
    """Sample GenerationContext for testing"""
    from llm.models import GenerationContext
    return GenerationContext(
        user_input="fantasy adventure",
        preferences={"difficulty": "medium", "length": "short"}
    )

@pytest.fixture
def sample_theme():
    """Sample Theme object for testing"""
    from llm.models import Theme
    return Theme(
        name="Dark Fantasy",
        description="A grim world of magic and monsters",
        mood="dark"
    )

@pytest.fixture
def sample_plot():
    """Sample Plot object for testing"""
    from llm.models import Plot
    return Plot(
        summary="Ancient evil awakens in forgotten ruins",
        objectives=["Find the ancient artifact", "Defeat the shadow lord"],
        setting_details="Crumbling castle filled with undead creatures"
    )

@pytest.fixture
def sample_game_mechanic():
    """Sample GameMechanic for testing"""
    from llm.models import GameMechanic
    return GameMechanic(
        name="Shadow Magic",
        description="Harness dark energy to cast spells",
        rules="Consume health to cast powerful shadow spells"
    )

@pytest.fixture
def sample_item():
    """Sample Item for testing"""
    from llm.models import Item
    return Item(
        name="Shadow Blade",
        description="A sword that drains life force",
        symbol="†",
        properties={"damage": 15, "life_drain": 3}
    )

# Mock fixtures for LLM testing
@pytest.fixture
def mock_llm():
    """Mock LLM for testing without API calls"""
    mock = Mock()
    mock.generate.return_value = "Mock LLM response"
    return mock

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response structure"""
    return {
        "choices": [{
            "message": {
                "content": "Mock response content"
            }
        }]
    }

# Validation fixtures
@pytest.fixture
def content_validator():
    """ContentValidator instance for testing"""
    from utils.validation import ContentValidator
    return ContentValidator()

# Integration test fixtures
@pytest.fixture
def test_world():
    """Test World instance with mocked LLM"""
    from llm.world import World
    world = World("test")
    # Mock the LLM to avoid API calls in tests
    world.llm = Mock()
    return world

@pytest.fixture
def game_entities():
    """Sample game entities for testing world tools"""
    return {
        "player": {"position": (5, 5), "symbol": "@", "name": "Hero"},
        "items": [
            {"position": (3, 3), "symbol": "!", "name": "Health Potion"},
            {"position": (7, 8), "symbol": "†", "name": "Magic Sword"}
        ],
        "enemies": [
            {"position": (10, 10), "symbol": "o", "name": "Goblin"},
            {"position": (15, 12), "symbol": "D", "name": "Dragon"}
        ]
    }

# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may be slow)"
    )
    config.addinivalue_line(
        "markers", "llm: marks tests that require LLM API calls"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )

# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark LLM tests
        if "llm" in item.nodeid and "mock" not in item.nodeid:
            item.add_marker(pytest.mark.llm)
