"""
Pytest configuration and shared fixtures for AiRogue tests.
"""
import socket
from unittest.mock import Mock

import pytest


def pytest_addoption(parser):
    """Register the explicit opt-in for tests that call the OpenAI API."""
    parser.addoption(
        "--run-requires-openai-api",
        action="store_true",
        default=False,
        help="run tests that require a real OpenAI API connection",
    )

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
        ascii_symbol="/",
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
    config.addinivalue_line(
        "markers", "requires_openai_api: marks tests that require the OpenAI API"
    )


def pytest_sessionstart(session):
    """Reject network access in the default, offline test suite.

    This is installed before test collection, so importing a module that opens
    a socket cannot silently make a paid API request.  The explicit OpenAI
    opt-in keeps the manually run end-to-end tests available.
    """
    if session.config.getoption("--run-requires-openai-api"):
        return

    original_socket = socket.socket

    class OfflineSocket(original_socket):
        def connect(self, address):
            raise RuntimeError("Network access is disabled during offline tests")

        def connect_ex(self, address):
            raise RuntimeError("Network access is disabled during offline tests")

    socket.socket = OfflineSocket

# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Skip real API tests unless they were explicitly requested."""
    if not config.getoption("--run-requires-openai-api"):
        skip_openai = pytest.mark.skip(
            reason="need --run-requires-openai-api option to run"
        )
        for item in items:
            if "requires_openai_api" in item.keywords:
                item.add_marker(skip_openai)

    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
