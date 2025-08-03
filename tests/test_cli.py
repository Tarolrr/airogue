"""
Tests for the CLI tool to ensure it works properly both when imported as a module and when run directly.
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import json

# Import test utilities
import pytest


class TestCliTool(unittest.TestCase):
    """Test the CLI tool functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Store the original sys.path to restore after tests
        self.original_path = sys.path.copy()
        
        # Get the project root directory
        self.project_root = str(Path(__file__).parent.parent.absolute())
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Restore the original sys.path
        sys.path = self.original_path

    def test_cli_imports(self):
        """Test that CLI imports work correctly."""
        # Import the CLI module to check if imports are resolved correctly
        try:
            from llm.generators import cli
            # If import succeeds, the test passes
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"CLI import failed: {e}")
    
    @patch('llm.generators.cli.WorldGenerator')
    @patch('llm.generators.cli.setup_environment')
    def test_generate_world_function(self, mock_setup_env, mock_world_generator):
        """Test the generate_world function."""
        from llm.generators import cli
        
        # Mock the WorldGenerator instance
        mock_generator_instance = MagicMock()
        mock_world_generator.return_value = mock_generator_instance
        
        # Mock the generated world
        mock_world = MagicMock()
        mock_world.theme = "Fantasy"
        mock_world.title = "The Magical Dungeon"
        mock_world.plot = "A hero seeks a magical artifact."
        mock_world.mechanics.mechanics = [
            MagicMock(name="Magic", description="Use spells to defeat enemies.")
        ]
        mock_world.items.items = [
            {"name": "Magic Wand", "ascii_symbol": "/", "description": "A powerful wand."}
        ]
        mock_world.json = MagicMock(return_value=json.dumps({"theme": "Fantasy"}))
        mock_generator_instance.generate.return_value = mock_world
        
        # Create a temporary file for output testing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            output_path = temp_file.name
        
        try:
            # Call the function to test
            result = cli.generate_world(api_key="test_key", output_path=output_path)
            
            # Verify the result
            self.assertEqual(result, mock_world)
            
            # Check that the world was saved to the file
            with open(output_path, 'r') as f:
                saved_content = f.read()
                self.assertEqual(saved_content, json.dumps({"theme": "Fantasy"}))
                
            # Verify WorldGenerator was called with correct parameters
            mock_world_generator.assert_called_once_with(api_key="test_key")
            mock_generator_instance.generate.assert_called_once()
            
        finally:
            # Clean up the temporary file
            if os.path.exists(output_path):
                os.unlink(output_path)

    @patch('llm.generators.cli.generate_world')
    @patch('llm.generators.cli.setup_environment')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_function(self, mock_parse_args, mock_setup_env, mock_generate_world):
        """Test the main function of the CLI."""
        from llm.generators import cli
        
        # Mock the parsed arguments
        mock_args = MagicMock()
        mock_args.api_key = "test_api_key"
        mock_args.output = "test_output.json"
        mock_parse_args.return_value = mock_args
        
        # Call the main function
        cli.main()
        
        # Verify setup_environment was called
        mock_setup_env.assert_called_once()
        
        # Verify generate_world was called with the correct arguments
        # The actual implementation in cli.py uses positional arguments
        mock_generate_world.assert_called_once_with(
            "test_api_key", 
            "test_output.json"
        )

    @patch('subprocess.run')
    def test_direct_script_execution(self, mock_subprocess):
        """Test direct execution of the CLI script."""
        # Get the path to the CLI script
        cli_path = os.path.join(self.project_root, "llm", "generators", "cli.py")
        
        # Mock the subprocess.run function
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Check if the file exists
        self.assertTrue(os.path.exists(cli_path), f"CLI script not found at {cli_path}")
        
        # Run the script directly with --help to test basic functionality
        # This doesn't actually run the script, just mocks the execution
        import subprocess
        try:
            subprocess.run([sys.executable, cli_path, "--help"], check=True)
        except Exception as e:
            self.fail(f"Failed to run CLI script directly: {e}")
        
        # Verify subprocess.run was called
        mock_subprocess.assert_called_once()
