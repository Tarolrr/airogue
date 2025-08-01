"""
Simple tests to debug import issues systematically.
"""
import pytest
import sys
from unittest.mock import patch, MagicMock


class TestImportDebugging:
    """Debug import issues step by step."""

    def test_llm_package_exists(self):
        """Test that llm package can be imported."""
        import llm
        assert llm is not None
    
    def test_llm_world_module_direct_import(self):
        """Test direct import of world module."""
        try:
            from llm import world
            assert world is not None
        except ImportError as e:
            pytest.fail(f"Could not import llm.world: {e}")
    
    def test_world_class_direct_import(self):
        """Test direct import of World class."""
        try:
            from llm.world import World
            assert World is not None
        except ImportError as e:
            pytest.fail(f"Could not import World class: {e}")
    
    def test_game_package_exists(self):
        """Test that game package can be imported."""
        import game
        assert game is not None
    
    def test_game_world_tools_direct_import(self):
        """Test direct import of world_tools module."""
        try:
            from game import world_tools
            assert world_tools is not None
        except ImportError as e:
            pytest.fail(f"Could not import game.world_tools: {e}")
    
    def test_new_world_function_direct_import(self):
        """Test direct import of new_world function."""
        try:
            from game.world_tools import new_world
            assert new_world is not None
        except ImportError as e:
            pytest.fail(f"Could not import new_world function: {e}")
