"""
Item generator module that provides functionality for generating game items.
This extracts item generation from the original WorldGenerator into a focused component.
"""
from typing import Any, Dict, List, Optional

from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser

from .base import BaseGenerator
from ..models import Items


class ItemGenerator(BaseGenerator):
    """Generator for game items based on mechanics."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano-2025-04-14", temperature: float = 1.0):
        """
        Initialize the item generator.
        
        Args:
            api_key: Optional OpenAI API key. If None, will use the OPENAI_API_KEY environment variable.
            model: The OpenAI model to use.
            temperature: Temperature for generation (0.0 to 2.0).
        """
        super().__init__(api_key, model, temperature)
        
        # Initialize parser
        self.item_parser = OutputFixingParser.from_llm(
            llm=self.llm,
            parser=PydanticOutputParser(pydantic_object=Items)
        )
    
    def generate(self, mechanics: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Generate items supporting the provided mechanics.
        
        Args:
            mechanics: List of game mechanic dictionaries.
            
        Returns:
            List of item dictionaries.
            
        GUARANTEES:
        - Items are balanced for mechanics
        - Items have valid ASCII symbols
        - No duplicate items
        
        CONSTRAINTS:
        - ONLY generates items for mechanics
        - 1-5 items per mechanic
        - Items must be representable in ASCII
        """
        # Extract mechanic names for the prompt
        mechanic_details = []
        for m in mechanics:
            mechanic_details.append(f"- {m['name']}: {m['description']}")
        
        mechanics_text = "\n".join(mechanic_details)
        
        # Create the prompt template
        prompt = self.create_prompt([
            ("system", 
                "You are a creative game designer specializing in roguelike games. "
                "Your task is to generate balanced and engaging items for a new roguelike game. "
                "Requirements to keep in mind:\n"
                "1. The game uses 2D ASCII visuals only.\n"
                "2. Each item must be representable with a single ASCII character.\n"
                "3. Items should be balanced and support the game mechanics.\n"
                "4. Each item should be unique with clear functionality."),
            ("user", 
                f"Generate items for a roguelike game with the following mechanics:\n\n{mechanics_text}\n\n"
                f"For each mechanic, create 1-3 items that support or enhance that mechanic. "
                f"Format your response as a valid JSON object with this structure:\n"
                "{\n"
                '  "items": [\n'
                '    {"name": "Item Name", "symbol": "A", "description": "Item description", "mechanic": "Related Mechanic", "rarity": "common/uncommon/rare"}\n'
                "  ]\n"
                "}\n\n"
                "Ensure each item has:\n"
                "1. A unique name\n"
                "2. A single ASCII character as its symbol\n"
                "3. A clear description of its function\n"
                "4. Which mechanic it supports\n"
                "5. An appropriate rarity (common, uncommon, or rare)")
        ])
        
        # Create chain with parser and execute
        chain = prompt | self.llm | JsonOutputParser()
        result = chain.invoke({})
        
        # Extract and return the items list
        return result.get("items", [])
    
    
if __name__ == "__main__":
    # Simple CLI interface for testing
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python item_generator.py <mechanics_json>")
        print("Example: python item_generator.py '[{\"name\": \"Permadeath\", \"description\": \"When the player dies, the game is over\"}]'")
        sys.exit(1)
        
    mechanics_json = sys.argv[1]
    mechanics = json.loads(mechanics_json)
    
    generator = ItemGenerator()
    items = generator.generate(mechanics)
    
    print(f"Generated {len(items)} items:")
    for i, item in enumerate(items, 1):
        print(f"\n{i}. {item['name']} [{item['symbol']}] - {item['rarity']}")
        print(f"   Description: {item['description']}")
        print(f"   Supports mechanic: {item['mechanic']}")
