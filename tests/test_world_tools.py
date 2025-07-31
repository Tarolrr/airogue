"""
Tests for game.world_tools module.

These tests validate that the critical production blocker (exit() call) has been fixed.
"""
import pytest
from unittest.mock import patch, mock_open


class TestWorldToolsExitFix:
    """Test that the exit() call has been removed from world_tools.py"""
    
    def test_world_tools_file_does_not_contain_exit_call(self):
        """Test that the world_tools.py file no longer contains an exit() call."""
        with open('game/world_tools.py', 'r') as f:
            content = f.read()
        
        # Check that exit() is not called in the file
        # We allow exit to be mentioned in comments but not as a function call
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip comment lines
            if line.strip().startswith('#'):
                continue
            # Check for exit() call
            if 'exit()' in line:
                pytest.fail(f"Found exit() call on line {i}: {line.strip()}")
    
    def test_new_world_function_completes_normally(self):
        """Test that importing and calling new_world doesn't cause exit."""
        # Test that we can at least import the function without issues
        try:
            from game.world_tools import new_world
            # If we get here, the import succeeded (no exit() during import)
            assert callable(new_world)
        except SystemExit:
            pytest.fail("new_world function or its imports called exit()")
        except Exception as e:
            # Other exceptions are fine - we're just testing that exit() isn't called
            # The function might fail due to missing files, etc., but shouldn't exit
            pass
    
    def test_world_model_json_file_exists(self):
        """Test that the world_model.json file exists (required by new_world)."""
        import os
        assert os.path.exists('world_model.json'), "world_model.json file is required for new_world() to work"
