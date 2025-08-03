"""
Tests for the theme generator module.
"""
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

from llm.generators.theme_generator import ThemeGenerator, SelectRandomThemeParser


class TestThemeGenerator(unittest.TestCase):
    """Test cases for ThemeGenerator."""
    
    @patch("llm.generators.theme_generator.BaseGenerator.llm", new_callable=PropertyMock)
    @patch("llm.generators.theme_generator.BaseGenerator.create_prompt")
    @patch("llm.generators.theme_generator.BaseGenerator.__init__", return_value=None)
    def test_generate_single(self, mock_init, mock_create_prompt, mock_llm_prop):
        """Test generate_single method."""
        # Setup
        mock_llm = MagicMock()
        mock_llm_prop.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Test theme"
        mock_prompt = MagicMock()
        mock_create_prompt.return_value = mock_prompt
        
        # Create the generator
        generator = ThemeGenerator()
        
        # Mock the pipe operation
        mock_prompt.__or__.return_value = MagicMock()
        mock_prompt.__or__.return_value.__or__ = MagicMock(return_value=mock_chain)
        
        # Call the method
        result = generator.generate_single()
        
        # Verify
        mock_create_prompt.assert_called_once()
        self.assertEqual(result, "Test theme")
        
    @patch("llm.generators.theme_generator.random.choice")
    @patch("llm.generators.theme_generator.JsonOutputParser")
    @patch("llm.generators.theme_generator.BaseGenerator.llm", new_callable=PropertyMock)
    @patch("llm.generators.theme_generator.BaseGenerator.create_prompt")
    @patch("llm.generators.theme_generator.BaseGenerator.__init__", return_value=None)
    def test_generate(self, mock_init, mock_create_prompt, mock_llm_prop, mock_json_parser, mock_choice):
        """Test generate method."""
        # Setup
        mock_llm = MagicMock()
        mock_llm_prop.return_value = mock_llm
        
        # Set up the JSON parser mock
        mock_parser_instance = MagicMock()
        mock_json_parser.return_value = mock_parser_instance
        
        # Set up the chain mocking
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"themes": ["Theme 1", "Theme 2"]}
        mock_prompt = MagicMock()
        mock_create_prompt.return_value = mock_prompt
        
        # Mock the random choice to return a fixed theme
        mock_choice.return_value = "Theme 1"
        
        # Mock the pipe operation
        mock_prompt.__or__.return_value = MagicMock()
        mock_prompt.__or__.return_value.__or__ = MagicMock(return_value=mock_chain)
        
        # Create the generator
        generator = ThemeGenerator()
        
        # Call the method
        result = generator.generate()
        
        # Verify
        mock_create_prompt.assert_called_once()
        mock_choice.assert_called_once_with(["Theme 1", "Theme 2"])
        self.assertEqual(result, "Theme 1")


if __name__ == "__main__":
    unittest.main()
