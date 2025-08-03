"""
Theme generator module that provides functionality for generating game themes.
This extracts theme generation from the original WorldGenerator into a focused component.
"""
from typing import Any, Dict, List, Optional

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import random

from .base import BaseGenerator


class SelectRandomThemeParser(JsonOutputParser):
    """Parser that selects a random theme from a list of generated themes."""
    
    def parse_result(self, text: str) -> str:
        list_ = super().parse_result(text)["themes"]
        return random.choice(list_)


class ThemeGenerator(BaseGenerator):
    """Generator for game themes."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano-2025-04-14", temperature: float = 1.0):
        """
        Initialize the theme generator.
        
        Args:
            api_key: Optional OpenAI API key. If None, will use the OPENAI_API_KEY environment variable.
            model: The OpenAI model to use.
            temperature: Temperature for generation (0.0 to 2.0).
        """
        super().__init__(api_key, model, temperature)
        
        # Initialize parsers
        self.theme_parser = SelectRandomThemeParser()
        
    def generate_single(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a single theme based on optional context.
        
        Args:
            context: Optional dictionary with context information like user preferences.
                    If None, a theme will be generated without constraints.
        
        Returns:
            String containing the generated theme.
            
        GUARANTEES: 
        - Theme is implementable in ASCII console
        - Theme has appropriate depth for short game experience
        
        CONSTRAINTS:
        - ONLY generates theme, never plots/mechanics/items
        - No themes requiring complex graphics
        """
        # Create the prompt template for a single theme
        prompt = self.create_prompt([
            ("system", 
                "You are a creative game designer specializing in console ASCII games. "
                "Your task is to generate an engaging theme for a new game. "
                "Requirements to keep in mind:\n"
                "1. The game uses 2D ASCII visuals only.\n"
                "2. The theme should be implementable without complex graphics.\n"
                "3. The theme should have enough depth for a short game experience (< 1 hour).\n"
                "4. The theme should be original and engaging."),
            ("user", 
                "Generate a unique theme for a console ASCII game. " 
                "The theme should be concise but descriptive.\n"
                + (f"User preferences to consider: {context}" if context else "") +
                "\nRespond with just the theme text, no additional formatting or explanation.")
        ])
        
        # Create chain and execute
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({}).strip()
    
    def generate(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a theme based on optional context (selects from multiple generated themes).
        
        Args:
            context: Optional dictionary with context information like user preferences.
                    If None, a random theme will be generated.
        
        Returns:
            String containing the selected theme.
            
        GUARANTEES: 
        - Theme is implementable in ASCII console
        - Theme has appropriate depth for short game experience
        
        CONSTRAINTS:
        - ONLY generates theme, never plots/mechanics/items
        - No themes requiring complex graphics
        """
        # Create the prompt template
        prompt = self.create_prompt([
            ("system", 
                "You are a creative game designer specializing in console ASCII games. "
                "Your task is to generate engaging themes for a new game. "
                "Requirements to keep in mind:\n"
                "1. The game uses 2D ASCII visuals only.\n"
                "2. The theme should be implementable without complex graphics.\n"
                "3. The theme should have enough depth for a short game experience (< 1 hour).\n"
                "4. The theme should be original and engaging."),
            ("user", 
                "Generate 5 different, unique themes for a console ASCII game. " 
                "Each theme should be distinct and orthogonal from the others. "
                "Format your response as a valid JSON object with this structure:\n"
                "{{\n"
                '  "themes": ["theme1", "theme2", "theme3", "theme4", "theme5"]\n'
                "}}\n"
                + (f"User preferences to consider: {context}" if context else ""))
        ])
        
        # Create chain with parser
        chain = prompt | self.llm | self.theme_parser
        
        # Execute the chain
        return chain.invoke({})
    
    
if __name__ == "__main__":
    # Simple CLI interface for testing
    import argparse
    parser = argparse.ArgumentParser(description="Generate themes for a console ASCII game")
    parser.add_argument(
        "--single",
        action="store_true",
        help="Generate a single theme directly instead of selecting from multiple"
    )
    parser.add_argument(
        "--context", 
        type=str,
        help="Optional context for theme generation"
    )
    args = parser.parse_args()
    
    generator = ThemeGenerator()
    if args.single:
        theme = generator.generate_single(args.context)
        print(f"Generated single theme: {theme}")
    else:
        theme = generator.generate(args.context)
        print(f"Generated theme (selected from multiple): {theme}")
