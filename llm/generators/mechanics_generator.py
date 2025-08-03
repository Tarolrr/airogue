"""
Mechanics generator module that provides functionality for generating game mechanics.
This extracts mechanics generation from the original WorldGenerator into a focused component.
"""
from typing import Dict, List, Optional

from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser

from .base import BaseGenerator
from ..models import GameMechanics


class MechanicsGenerator(BaseGenerator):
    """Generator for game mechanics based on themes, titles, and plots."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano-2025-04-14", temperature: float = 1.0):
        """
        Initialize the mechanics generator.
        
        Args:
            api_key: Optional OpenAI API key. If None, will use the OPENAI_API_KEY environment variable.
            model: The OpenAI model to use.
            temperature: Temperature for generation (0.0 to 2.0).
        """
        super().__init__(api_key, model, temperature)
        
        # Initialize parser
        self.gm_parser = OutputFixingParser.from_llm(
            llm=self.llm,
            parser=PydanticOutputParser(pydantic_object=GameMechanics)
        )
    
    def generate(self, theme: str, title: str, plot: str) -> List[Dict[str, str]]:
        """
        Generate game mechanics based on theme, title and plot.
        
        Args:
            theme: The game theme.
            title: The game title.
            plot: The game plot.
            
        Returns:
            List of game mechanic dictionaries.
            
        GUARANTEES:
        - Mechanics are consistent with theme and plot
        - No duplicate mechanics
        - All implementable in ASCII roguelike
        
        CONSTRAINTS:
        - ONLY generates mechanics, never themes/plots/items
        - 2-7 mechanics (game balance requirement)
        - No mechanics requiring sound (engine limitation)
        """
        # Create the prompt template
        prompt = self.create_prompt([
            ("system", 
                "You are a creative game designer specializing in console ASCII games. "
                "Your task is to generate engaging game mechanics for a new game. "
                "Requirements to keep in mind:\n"
                "1. The game uses 2D ASCII visuals only.\n"
                "2. The game engine does not support sound.\n"
                "3. All mechanics must be implementable in a terminal-based game.\n"
                "4. Each mechanic should be unique and contribute to gameplay depth."),
            ("user", 
                f"Generate 2-3 detailed game mechanics for a minimalistic console game with the title '{title}' and theme '{theme}'. "
                f"The mechanics should align with this plot: '{plot}'. "
                f"Format your response as a valid JSON object with this structure:\n"
                "{{\n"
                '  "mechanics": [\n'
                '    {{"name": "Mechanic Name", "description": "Detailed description of how the mechanic works", "rules": "Specific rules for this mechanic"}}\n'
                "  ]\n"
                "}}")
        ])
        
        # Create chain with parser and execute
        chain = prompt | self.llm | JsonOutputParser()
        result = chain.invoke({})
        
        # Extract and return the mechanics list
        return result.get("mechanics", [])
    
    
if __name__ == "__main__":
    # Simple CLI interface for testing
    import sys
    if len(sys.argv) < 4:
        print("Usage: python mechanics_generator.py <theme> <title> <plot>")
        sys.exit(1)
        
    theme = sys.argv[1]
    title = sys.argv[2]
    plot = sys.argv[3]
    
    generator = MechanicsGenerator()
    mechanics = generator.generate(theme, title, plot)
    
    print(f"Generated mechanics for '{title}':")
    for i, mechanic in enumerate(mechanics, 1):
        print(f"\n{i}. {mechanic['name']}")
        print(f"   Description: {mechanic['description']}")
        print(f"   Rules: {mechanic['rules']}")
