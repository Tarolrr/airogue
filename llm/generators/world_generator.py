"""
World generator module that provides functionality for generating game worlds.
This module orchestrates the generation process using specialized generators
for themes, plots, mechanics, and items.
"""
from typing import Any, Dict, List, Optional

from .base import BaseGenerator
from .theme_generator import ThemeGenerator
from .title_generator import TitleGenerator
from .plot_generator import PlotGenerator
from .mechanics_generator import MechanicsGenerator
from .item_generator import ItemGenerator
from ..models import WorldModel


# Removed SelectRandomThemeParser - now in ThemeGenerator


class WorldGenerator(BaseGenerator):
    """Generator for complete game worlds including theme, plot, mechanics and items.
    This class orchestrates the generation process using specialized generators."""
    
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
        
        # Initialize component generators
        self.theme_generator = ThemeGenerator(api_key, model, temperature)
        self.title_generator = TitleGenerator(api_key, model, temperature)
        self.plot_generator = PlotGenerator(api_key, model, temperature)
        self.mechanics_generator = MechanicsGenerator(api_key, model, temperature)
        self.item_generator = ItemGenerator(api_key, model, temperature)
    
    def generate_themes(self) -> Dict[str, List[str]]:
        """
        Generate a list of potential game themes.
        
        Returns:
            Dictionary with a 'themes' key containing a list of theme strings.
        """
        # Generate 5 themes and return as a dictionary
        themes = []
        for _ in range(5):
            themes.append(self.theme_generator.generate_single())
        
        return {"themes": themes}
    
    def generate_title(self, theme: str) -> str:
        """
        Generate a title based on a theme.
        
        Args:
            theme: The game theme.
            
        Returns:
            String containing the generated title.
        """
        title = self.title_generator.generate(theme)
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
        plot = self.plot_generator.generate(theme, title)
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
        mechanics = self.mechanics_generator.generate(theme, title, plot)
        
        self.design_doc += f"Game Mechanics: {len(mechanics)} mechanics generated\n"
        for m in mechanics:
            self.design_doc += f"- {m['name']}: {m['description']}\n"
        
        return mechanics
    
    def generate_items(self, mechanics: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Generate game items based on mechanics.
        
        Args:
            mechanics: List of game mechanic dictionaries.
            
        Returns:
            List of item dictionaries.
        """
        items = self.item_generator.generate(mechanics)
        
        self.design_doc += f"Items: {len(items)} items generated\n"
        for item in items:
            self.design_doc += f"- {item['name']} [{item['symbol']}]: {item['description']}\n"
        
        return items
    
    def generate(self, context: Optional[str] = None) -> WorldModel:
        """
        Generate a complete game world.
        
        Returns:
            WorldModel object containing all generated content.
        """
        # Get a theme - select one from the generated themes
        theme = self.theme_generator.generate(context=context)
        
        # Generate title
        title = self.title_generator.generate(theme)
        
        # Generate plot
        plot = self.plot_generator.generate(theme, title)
        
        # Generate game mechanics
        mechanics = self.mechanics_generator.generate(theme, title, plot)
        
        # Generate items using the game mechanics
        items = self.item_generator.generate(mechanics)
        
        # Create and return the world model
        return WorldModel(
            theme=theme,
            title=title,
            plot=plot,
            mechanics={"mechanics": mechanics},
            items={"items": items}
        )


def main(api_key: Optional[str] = None, context: Optional[str] = None):
    """
    Run the world generator as a standalone tool.
    
    Args:
        api_key: Optional OpenAI API key. If None, will use OPENAI_API_KEY environment variable.
    """
    generator = WorldGenerator(api_key=api_key)
    print("Generating world...")
    world = generator.generate(context=context)
    
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
        print(f"- {item.name} [{item.ascii_symbol}]: {item.description}")
    
    return world


if __name__ == "__main__":
    import os
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate a roguelike game world")
    parser.add_argument("--api-key", type=str, help="OpenAI API key (if not provided, will use OPENAI_API_KEY env var)")
    parser.add_argument("--context", type=str, help="Context for the world generator")
    parser.add_argument("--output", type=str, help="Output file path for the generated world (JSON format)")
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: No OpenAI API key provided. Either set the OPENAI_API_KEY environment variable or use --api-key.")
        exit(1)
    
    world = main(api_key, args.context)
    
    # Save to file if output path specified
    if args.output:
        import json
        with open(args.output, "w") as f:
            f.write(world.json(indent=2))
        print(f"\nWorld saved to {args.output}")
