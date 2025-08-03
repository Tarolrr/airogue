"""
End-to-end tests for the WorldGenerator class.
Tests the complete world generation pipeline from input to output.

These tests include real LLM calls and are marked with 'requires_openai_api'
so they are skipped by default. Run with '--run-requires-openai-api' to include them.
"""
import pytest
from unittest.mock import patch, MagicMock
import json
import os
from pathlib import Path

from llm.models import WorldModel, GameMechanics, Items
from llm.generators.world_generator import WorldGenerator


# Define a custom pytest marker for tests that require OpenAI API
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_openai_api: mark test as requiring OpenAI API access"
    )

# Add a command line option to run these tests
def pytest_addoption(parser):
    parser.addoption(
        "--run-requires-openai-api", action="store_true", default=False, help="run tests that require OpenAI API"
    )

# Skip the marked tests unless explicitly requested
def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-requires-openai-api"):
        skip_openai = pytest.mark.skip(reason="need --run-requires-openai-api option to run")
        for item in items:
            if "requires_openai_api" in item.keywords:
                item.add_marker(skip_openai)


class TestWorldGeneratorE2E:
    """End-to-end tests for WorldGenerator."""
    
    @pytest.mark.requires_openai_api
    def test_world_generation_real_llm(self):
        """
        End-to-end test using a real LLM call.
        
        This test is marked with requires_openai_api and will be skipped
        unless pytest is run with --run-requires-openai-api flag.
        """
        # Skip if no API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY environment variable not set")
        
        # Create the generator with a faster/cheaper model
        generator = WorldGenerator(model="gpt-3.5-turbo", temperature=0.7)
        
        # Generate a complete world
        result = generator.generate()
        
        # Verify the world model structure
        assert isinstance(result, WorldModel)
        assert len(result.theme) > 0
        assert len(result.title) > 0
        assert len(result.plot) > 0
        
        # Check game mechanics
        assert isinstance(result.mechanics, GameMechanics)
        assert isinstance(result.mechanics.mechanics, list)
        assert len(result.mechanics.mechanics) > 0
        
        # Check mechanics have meaningful content
        for mechanic in result.mechanics.mechanics:
            assert len(mechanic.name) > 0
            assert len(mechanic.description) > 0
        
        # Check items
        assert isinstance(result.items, Items)
        assert isinstance(result.items.items, list)
        
        # Check items have meaningful content
        for item in result.items.items:
            assert len(item.name) > 0
            assert len(item.ascii_symbol) > 0
            assert len(item.description) > 0
            
        # Log the generated content for inspection
        print(f"\n===== GENERATED WORLD =====\n")
        print(f"Theme: {result.theme}")
        print(f"Title: {result.title}")
        print(f"Plot: {result.plot}")
        print("\nGame Mechanics:")
        for mechanic in result.mechanics.mechanics:
            print(f"- {mechanic.name}: {mechanic.description}")
        print("\nItems:")
        for item in result.items.items:
            print(f"- {item.name} [{item.ascii_symbol}]: {item.description}")


    @pytest.mark.requires_openai_api
    def test_world_generation_save_to_file(self):
        """
        End-to-end test that generates a world and saves it to a file for reference.
        
        This is useful for generating reference data that can be used for comparison
        in future tests or for manual inspection.
        """
        # Skip if no API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY environment variable not set")
        
        # Create a directory for test output if it doesn't exist
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Create the generator with a faster/cheaper model
        generator = WorldGenerator(model="gpt-3.5-turbo", temperature=0.7)
        
        # Generate a complete world
        result = generator.generate()
        
        # Save the generated world to a file for inspection and reference
        output_file = output_dir / "generated_world.json"
        with open(output_file, "w") as f:
            # Convert the Pydantic model to dict and then to JSON
            world_dict = {
                "theme": result.theme,
                "title": result.title,
                "plot": result.plot,
                "mechanics": [
                    {"name": mechanic.name, "description": mechanic.description}
                    for mechanic in result.mechanics.mechanics
                ],
                "items": [
                    {
                        "name": item.name, 
                        "ascii_symbol": item.ascii_symbol, 
                        "description": item.description
                    }
                    for item in result.items.items
                ]
            }
            json.dump(world_dict, f, indent=4)
            
        print(f"Generated world saved to {output_file}")
        
        # Basic verification that the world was generated correctly
        assert isinstance(result, WorldModel)
        assert isinstance(result.theme, str)
        assert isinstance(result.title, str)
        assert isinstance(result.plot, str)
        assert len(result.mechanics.mechanics) > 0
        assert len(result.items.items) >= 0  # Some mechanics may not require items
