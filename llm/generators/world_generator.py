"""
World generator module that provides functionality for generating game worlds.
This module extracts the core world generation functionality from the original world.py
into a reusable, modular component that can be run separately.
"""
import random
from operator import itemgetter
from typing import Any, Dict, List, Optional

from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_core.runnables.passthrough import identity

from .base import BaseGenerator
from ..models import GameMechanics, Items, Themes, WorldModel


class SelectRandomThemeParser(JsonOutputParser):
    """Parser that selects a random theme from a list of generated themes."""
    
    def parse_result(self, text: str) -> str:
        list_ = super().parse_result(text)["themes"]
        return random.choice(list_)


class WorldGenerator(BaseGenerator):
    """Generator for complete game worlds including theme, plot, mechanics and items."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano-2025-04-14", temperature: float = 1.0):
        """
        Initialize the world generator.
        
        Args:
            api_key: Optional OpenAI API key. If None, will use the OPENAI_API_KEY environment variable.
            model: The OpenAI model to use.
            temperature: Temperature for generation (0.0 to 2.0).
        """
        super().__init__(api_key, model, temperature)
        self.design_doc = ""
        
        # Initialize parsers
        self.theme_parser = SelectRandomThemeParser(pydantic_object=Themes)
        self.item_parser = OutputFixingParser.from_llm(
            llm=self.llm,
            parser=PydanticOutputParser(pydantic_object=Items)
        )
        self.gm_parser = OutputFixingParser.from_llm(
            llm=self.llm,
            parser=PydanticOutputParser(pydantic_object=GameMechanics)
        )
        
        # Create the standard prompt template
        self.prompt = self.create_prompt([
            ("system", 
                "You are a creative game designer specializing in roguelike games. "
                "Your task is to assist in the design of a new roguelike game. "
                "There are certain requirements that you should keep in mind at all times while designing the game:\n"
                "1. The genre is roguelike, singleplayer, minimalistic.\n"
                "2. The game uses 2D ASCII engine.\n"
                "3. The game engine does not support sound.\n"
                "4. The game is terminal-only (engine supports drawing environment with different symbols).\n"
                "5. The game experience should be short. No more than an hour."),
            ("user", "{input}"),
        ])
        
        # Create reusable chains
        self.chain = {
            "input": lambda x: x["input"]
        } | self.prompt | self.llm | StrOutputParser()
        
        self.partial_chain = {
            "input": lambda x: x["input"]
        } | self.prompt | self.llm
    
    def generate_themes(self) -> Dict[str, List[str]]:
        """
        Generate a list of potential game themes.
        
        Returns:
            Dictionary with a 'themes' key containing a list of theme strings.
        """
        themes_prompt = {
            "input": (
                f"Generate different, \"orthogonal\" themes for a game."
                f"\n{self.theme_parser.get_format_instructions()}"
            )
        }
        chain = self.partial_chain | self.theme_parser
        return chain.invoke(themes_prompt)
    
    def generate_title(self, theme: str) -> str:
        """
        Generate a title based on a theme.
        
        Args:
            theme: The game theme.
            
        Returns:
            String containing the generated title.
        """
        title_prompt = {
            "input": f"Generate a title for a game with the following theme {theme}."
        }
        
        title = self.chain.invoke(title_prompt)
        self.design_doc += f"Theme: {theme}\n"
        self.design_doc += f"Title: {title}\n"
        return title
    
    def generate_plot(self, theme: str, title: str) -> str:
        """
        Generate a plot based on a theme and title.
        
        Args:
            theme: The game theme.
            title: The game title.
            
        Returns:
            String containing the generated plot.
        """
        plot_prompt = {
            "input": (
                f"Generate a plot for a game with title {title} and the following overall theme: {theme}."
            )
        }
        plot = self.chain.invoke(plot_prompt)
        self.design_doc += f"Plot: {plot}\n"
        return plot
    
    def generate_game_mechanics(self, theme: str, title: str, plot: str) -> List[Dict[str, str]]:
        """
        Generate game mechanics based on theme, title and plot.
        
        Args:
            theme: The game theme.
            title: The game title.
            plot: The game plot.
            
        Returns:
            List of game mechanic dictionaries.
        """
        # For real LLM calls, we need a simpler approach to avoid schema confusion
        game_mechanics_prompt = {
            "input": (
                f"Generate 2-3 detailed game mechanics for a minimalistic console roguelike game with the title '{title}' and theme '{theme}'. "
                f"The mechanics should align with this plot: '{plot}'. "
                f"Format your response as a valid JSON object with this structure:\n"
                f"{{\n"
                f"  \"mechanics\": [\n"
                f"    {{ \"name\": \"Mechanic Name\", \"description\": \"Detailed mechanic description\" }},\n"
                f"    {{ \"name\": \"Another Mechanic\", \"description\": \"Another detailed description\" }}\n"
                f"  ]\n"
                f"}}\n"
                f"IMPORTANT: Return ONLY the JSON with no additional text, explanations, or formatting."
            )
        }
        try:
            # First try using the regular parser
            chain = self.partial_chain | self.gm_parser
            result = chain.invoke(game_mechanics_prompt)
            return result.mechanics
        except Exception as e:
            # If parsing fails, try a more direct approach
            print(f"Parser error: {e}. Falling back to direct JSON parsing.")
            chain = self.partial_chain | StrOutputParser()
            raw_result = chain.invoke(game_mechanics_prompt)
            
            # Try to parse the raw JSON
            try:
                parsed = json.loads(raw_result)
                if "mechanics" in parsed and isinstance(parsed["mechanics"], list):
                    return parsed["mechanics"]
                else:
                    raise ValueError(f"Invalid mechanics format in: {parsed}")
            except json.JSONDecodeError:
                # As a last resort, return a default mechanic
                print(f"Failed to parse mechanic JSON. Using fallback mechanic.")
                return [{
                    "name": f"Adventure in {theme}",
                    "description": f"Explore the world of {title} with unique challenges and discoveries."
                }]
    
    def generate_items(self, game_mechanic: GameMechanics) -> List[Dict[str, Any]]:
        """
        Generate items based on game mechanics.
        
        Args:
            game_mechanic: The game mechanics object.
            
        Returns:
            List of item dictionaries.
        """
        items_prompt = {
            "input": (
                "We're in the process of a game design. "
                "You will be supplied with the design document and one of the game mechanics. "
                "Your job is to come up with a list of 0 to 3 items that will be used in the game. "
                "They should be strictly aligned with the game mechanic given. "
                "If the game mechanic does not have anything to do with the items, give an empty list.\n"
                "Here's the design document:\n"
                f"{self.design_doc}\n\n"
                f"Here's the game mechanic:\n"
                f"{str(game_mechanic)}\n\n"
                f"{self.item_parser.get_format_instructions()}"
            )
        }
        
        chain = self.partial_chain | self.item_parser
        return chain.invoke(items_prompt).items
    
    def generate(self) -> WorldModel:
        """
        Generate a complete world model.
        
        Returns:
            WorldModel object containing all generated content.
        """
        # Get a theme - SelectRandomThemeParser already returns a single theme string
        theme = self.generate_themes()
        
        # Generate title
        title = self.generate_title(theme)
        
        # Generate plot
        plot = self.generate_plot(theme, title)
        
        # Generate game mechanics
        mechanics_list = self.generate_game_mechanics(theme, title, plot)
        
        # Ensure mechanics_list contains proper GameMechanic objects
        # If we get a list of dicts, convert them to GameMechanic objects
        processed_mechanics = []
        for mech in mechanics_list:
            if isinstance(mech, dict):
                processed_mechanics.append(GameMechanic(**mech))
            else:
                processed_mechanics.append(mech)
        
        mechanics = GameMechanics(mechanics=processed_mechanics)
        
        # Generate items for each mechanic
        all_items = []
        for mechanic in processed_mechanics:
            # Create a GameMechanics object with a single mechanic
            mechanic_obj = GameMechanics(mechanics=[mechanic])
            items = self.generate_items(mechanic_obj)
            all_items.extend(items)
        
        # Create and return the world model
        return WorldModel(
            theme=theme,
            title=title,
            plot=plot,
            mechanics=mechanics,
            items=Items(items=all_items),
            global_entities={}  # Empty for now, will be filled by the game
        )


def main(api_key: Optional[str] = None):
    """
    Run the world generator as a standalone tool.
    
    Args:
        api_key: Optional OpenAI API key. If None, will use OPENAI_API_KEY environment variable.
    """
    generator = WorldGenerator(api_key=api_key)
    print("Generating world...")
    world = generator.generate()
    
    # Print the generated world
    print("\n===== GENERATED WORLD =====\n")
    print(f"Theme: {world.theme}")
    print(f"Title: {world.title}")
    print(f"Plot: {world.plot}")
    
    print("\nGame Mechanics:")
    for mechanic in world.mechanics.mechanics:
        print(f"- {mechanic.name}: {mechanic.description}")
    
    print("\nItems:")
    for item in world.items.items:
        print(f"- {item['name']} [{item['ascii_symbol']}]: {item['description']}")
    
    return world


if __name__ == "__main__":
    import os
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate a roguelike game world")
    parser.add_argument("--api-key", type=str, help="OpenAI API key (if not provided, will use OPENAI_API_KEY env var)")
    parser.add_argument("--output", type=str, help="Output file path for the generated world (JSON format)")
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: No OpenAI API key provided. Either set the OPENAI_API_KEY environment variable or use --api-key.")
        exit(1)
    
    world = main(api_key)
    
    # Save to file if output path specified
    if args.output:
        import json
        with open(args.output, "w") as f:
            f.write(world.json(indent=2))
        print(f"\nWorld saved to {args.output}")
