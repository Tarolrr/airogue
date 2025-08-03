"""World generator wrapper for backward compatibility.

This module wraps the new modular world generator for backward compatibility.
It uses the same interface as the original World class but delegates to the
WorldGenerator class for the actual generation logic.
"""
import os
from typing import Any, Dict, List, Optional, Union

from colored import attr, fg

from .models import GameMechanics, Items, Themes, WorldModel
from .generators.world_generator import WorldGenerator


class World:
    """World generator class for backward compatibility.
    
    This class maintains the same interface as the original World class but
    delegates to the WorldGenerator class for the actual generation logic.
    """
    
    def __init__(self, setting: Any, api_key: Optional[str] = None):
        """Initialize the World generator.
        
        Args:
            setting: Game setting (maintained for backward compatibility).
            api_key: Optional OpenAI API key. If None, uses OPENAI_API_KEY environment variable.
        """
        self.setting = setting
        self.setting_details = ""
        self.design_doc = ""
        
        # Create the actual generator
        self.generator = WorldGenerator(api_key=api_key)
        
        # For logging purposes
        if hasattr(self.generator.llm, "__str__"):
            print(self.generator.llm)

    def theme(self) -> str:
        """Generate a theme for the game.
        
        Returns:
            A string representing the theme.
        """
        # Use the generator's theme generation functionality
        themes_result = self.generator.generate_themes()
        theme = themes_result["themes"][0] if isinstance(themes_result, dict) else themes_result
        return theme
    
    def generate_title(self, theme: str) -> str:
        """Generate a title based on the theme.
        
        Args:
            theme: The theme for the game.
            
        Returns:
            A string representing the title.
        """
        title = self.generator.generate_title(theme)
        self.design_doc += f"Theme: {theme}\n"
        self.design_doc += f"Title: {title}\n"
        return title
    
    def generate_plot(self, theme: str, title: str) -> str:
        """Generate a plot based on the theme and title.
        
        Args:
            theme: The theme for the game.
            title: The title of the game.
            
        Returns:
            A string representing the plot.
        """
        plot = self.generator.generate_plot(theme, title)
        self.design_doc += f"Plot: {plot}\n"
        return plot
    
    def generate_game_mechanics(self, theme: str, title: str, plot: str) -> List[Dict[str, str]]:
        """Generate game mechanics based on the theme, title, and plot.
        
        Args:
            theme: The theme for the game.
            title: The title of the game.
            plot: The plot of the game.
            
        Returns:
            A list of game mechanics.
        """
        return self.generator.generate_game_mechanics(theme, title, plot)
    
    def generate_items(self, game_mechanic: Union[Dict[str, str], GameMechanics]) -> List[Dict[str, Any]]:
        """Generate items based on a game mechanic.
        
        Args:
            game_mechanic: A game mechanic object or dictionary.
            
        Returns:
            A list of items.
        """
        # Convert dictionary to GameMechanics object if necessary
        if isinstance(game_mechanic, dict):
            game_mechanic = GameMechanics(mechanics=[game_mechanic])
            
        return self.generator.generate_items(game_mechanic)
    
    def generate_world(self) -> WorldModel:
        """Generate a complete world model.
        
        Returns:
            A WorldModel object containing the generated world.
        """
        # Directly delegate to the generator
        return self.generator.generate()

    def print_world(self, theme, title, plot, mechanics, items):
        print(fg("green") + attr("bold") + "Theme: " + attr("reset"), end="")
        print(fg("white") + theme)
        print(attr("reset"))
        print()

        print(fg("green") + attr("bold") + "Title: " + attr("reset"), end="")
        print(fg("white") + title)
        print(attr("reset"))
        print()

        print(fg("green") + attr("bold") + "Plot: " + attr("reset"), end="")
        print(fg("white") + plot)
        print(attr("reset"))
        print()

        print(fg("green") + attr("bold") + "Game mechanics:", end="")
        print(attr("reset"))
        for line in mechanics:
            print(fg("yellow") + "- ", end="")
            print(fg("white") + str(line))
            print(attr("reset"))
        print()

        print(fg("green") + attr("bold") + "Items:", end="")
        print(attr("reset"))
        for line in items:
            print(fg("yellow") + "- ", end="")
            print(fg("white") + str(line))
            print(attr("reset"))
        print()

        # print(fg("cyan") + "  - ", end="")
        # print(fg("blue") + str(item))

# Simple command-line interface if run directly
if __name__ == "__main__":
    import sys
    import argparse
    import dotenv
    
    # First try to load .env files
    if os.path.exists(".env"):
        dotenv.load_dotenv()
        
    home_env = os.path.join(os.path.expanduser("~"), ".airogue.env")
    if os.path.exists(home_env):
        dotenv.load_dotenv(home_env)
        
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate a roguelike game world")
    parser.add_argument("--api-key", type=str, help="OpenAI API key (if not provided, will use OPENAI_API_KEY env var)")
    parser.add_argument("--env-file", type=str, help="Path to .env file with OPENAI_API_KEY")
    args = parser.parse_args()
    
    # Load from specific env file if provided
    if args.env_file and os.path.exists(args.env_file):
        dotenv.load_dotenv(args.env_file)
        
    # Get API key
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: No OpenAI API key provided. Use one of these methods:")
        print("1. Set the OPENAI_API_KEY environment variable")
        print("2. Create a .env file with OPENAI_API_KEY=your-key")
        print("3. Create a ~/.airogue.env file with OPENAI_API_KEY=your-key")
        print("4. Use the --api-key command line argument")
        print("5. Specify a custom .env file with --env-file")
        sys.exit(1)
        
    # Initialize the world with the API key
    world = World(None, api_key=api_key)
    
    # Generate content step by step
    theme = world.theme()
    print(f"Theme: {theme}")
    
    title = world.generate_title(theme)
    print(f"Title: {title}")
    
    plot = world.generate_plot(theme, title)
    print(f"Plot: {plot}")
    
    game_mechanics = world.generate_game_mechanics(theme, title, plot)
    print("Game Mechanics:")
    for mechanic in game_mechanics:
        print(f"- {mechanic}")
        
    # Generate items for each game mechanic
    total_items = []
    for mechanic in game_mechanics:
        items = world.generate_items(mechanic)
        total_items.extend(items)
        
    print("Items:")
    for item in total_items:
        print(f"- {item['name']} [{item['ascii_symbol']}]: {item['description']}")
        
    # Print the complete world
    world.print_world(theme, title, plot, game_mechanics, total_items)
