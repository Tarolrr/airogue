"""
Plot generator module that provides functionality for generating game plots.
This extracts plot generation from the original WorldGenerator into a focused component.
"""
from typing import Optional

from langchain_core.output_parsers import StrOutputParser

from .base import BaseGenerator


class PlotGenerator(BaseGenerator):
    """Generator for game plots based on themes and titles."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano-2025-04-14", temperature: float = 1.0):
        """
        Initialize the plot generator.
        
        Args:
            api_key: Optional OpenAI API key. If None, will use the OPENAI_API_KEY environment variable.
            model: The OpenAI model to use.
            temperature: Temperature for generation (0.0 to 2.0).
        """
        super().__init__(api_key, model, temperature)
    
    def generate(self, theme: str, title: str) -> str:
        """
        Generate a plot based on theme and title.
        
        Args:
            theme: The game theme.
            title: The game title.
            
        Returns:
            String containing the generated plot.
            
        GUARANTEES:
        - Plot complements theme and title
        - Plot has proper narrative arc for roguelike
        
        CONSTRAINTS:
        - ONLY generates plot, never themes/mechanics/items
        - Plot must be completable in < 1 hour gameplay
        - No complex branching narratives (engine limitation)
        """
        # Create the prompt template
        prompt = self.create_prompt([
            ("system", 
                "You are a creative game designer specializing in roguelike games. "
                "Your task is to generate engaging plots for a new roguelike game. "
                "Requirements to keep in mind:\n"
                "1. The game is a roguelike with a short playtime (< 1 hour).\n"
                "2. The plot should have a clear goal and narrative arc suitable for the genre.\n"
                "3. The plot should be linear - no complex branching narratives.\n"
                "4. The plot should complement and enhance the provided theme and title."),
            ("user", 
                f"Generate a plot for a roguelike game with title '{title}' and theme '{theme}'. "
                f"The plot should be concise but engaging, and completable within a one-hour gameplay session. "
                f"Focus on creating a compelling narrative that works well with the theme.")
        ])
        
        # Create and execute chain
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({})
    
    
if __name__ == "__main__":
    # Simple CLI interface for testing
    import sys
    if len(sys.argv) < 3:
        print("Usage: python plot_generator.py <theme> <title>")
        sys.exit(1)
        
    theme = sys.argv[1]
    title = sys.argv[2]
    
    generator = PlotGenerator()
    plot = generator.generate(theme, title)
    print(f"Generated plot for '{title}' with theme '{theme}':\n{plot}")
