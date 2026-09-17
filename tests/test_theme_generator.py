"""
Tests for the theme generator module.
"""
import unittest
from unittest.mock import MagicMock, patch

from llm.generators.theme_generator import ThemeGenerator, SelectRandomThemeParser


class TestThemeGenerator(unittest.TestCase):
    """Test cases for ThemeGenerator."""
    
    def test_generate_single_strips_chain_result(self):
        """Test generate_single method."""
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "  Test theme  "
        mock_prompt = MagicMock()
        generator = ThemeGenerator()
        generator.create_prompt = MagicMock(return_value=mock_prompt)
        generator._llm = MagicMock()
        mock_prompt.__or__.return_value = MagicMock()
        mock_prompt.__or__.return_value.__or__ = MagicMock(return_value=mock_chain)

        result = generator.generate_single()

        generator.create_prompt.assert_called_once()
        mock_chain.invoke.assert_called_once_with({})
        self.assertEqual(result, "Test theme")

    @patch("llm.generators.theme_generator.random.choice")
    def test_parser_selects_theme_from_valid_json(self, mock_choice):
        parser = SelectRandomThemeParser()
        mock_choice.return_value = "Theme 1"

        result = parser.parse('{"themes": ["Theme 1", "Theme 2"]}')

        mock_choice.assert_called_once_with(["Theme 1", "Theme 2"])
        self.assertEqual(result, "Theme 1")

    def test_generate_delegates_to_theme_parser(self):
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Theme 1"
        mock_prompt = MagicMock()
        mock_parser = MagicMock()
        generator = ThemeGenerator()
        generator.create_prompt = MagicMock(return_value=mock_prompt)
        generator._llm = MagicMock()
        generator.theme_parser = mock_parser
        mock_prompt.__or__.return_value = MagicMock()
        mock_prompt.__or__.return_value.__or__ = MagicMock(return_value=mock_chain)

        result = generator.generate()

        generator.create_prompt.assert_called_once()
        mock_chain.invoke.assert_called_once_with({})
        self.assertEqual(result, "Theme 1")


if __name__ == "__main__":
    unittest.main()
