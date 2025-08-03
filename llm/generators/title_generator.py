"""
Title generator module that provides functionality for generating game titles.
This extracts title generation from the original WorldGenerator into a focused component.
"""
from typing import Optional

from langchain_core.output_parsers import StrOutputParser

from .base import BaseGenerator


class TitleGenerator(BaseGenerator):
    """Generator for game titles based on themes."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano-2025-04-14", temperature: float = 1.0):
        """
        Initialize the title generator.
        
        Args:
            api_key: Optional OpenAI API key. If None, will use the OPENAI_API_KEY environment variable.
            model: The OpenAI model to use.
            temperature: Temperature for generation (0.0 to 2.0).
        """
        super().__init__(api_key, model, temperature)
    
    def generate(self, theme: str) -> str:
        """
        Generate a title based on a theme.
        
        Args:
            theme: The game theme.
            
        Returns:
            String containing the generated title.
            
        GUARANTEES:
        - Title is consistent with provided theme
        - Always returns a non-empty string
        
        CONSTRAINTS:
        - ONLY generates a title based on theme
        """
        # Create the prompt template
        prompt = self.create_prompt([
            ("system", 
                "You are a creative game designer specializing in console ASCII games. "
                "Your task is to generate an engaging title for a new game. "
                "The title should be memorable, concise, and reflect the theme."),
            ("user", 
                f"Generate a compelling title for a console ASCII game with the following theme: '{theme}'. "
                f"The title should be catchy, appropriate for the genre, and reflect the theme without being too generic. "
                f"Respond with just the title, nothing else.")
        ])
        
        # Create and execute chain
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({}).strip()
    
    
if __name__ == "__main__":
    # Simple CLI interface for testing
    import sys
    if len(sys.argv) < 2:
        print("Usage: python title_generator.py <theme>")
        sys.exit(1)
        
    theme = sys.argv[1]
    
    generator = TitleGenerator()
    title = generator.generate(theme)
    print(f"Generated title for theme '{theme}':\n{title}")
