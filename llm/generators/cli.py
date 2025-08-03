#!/usr/bin/env python
"""
Command-line interface for the world generator.
This script allows the world generator to be run as a standalone tool.
"""
import os
import sys
import json
import argparse
from typing import Optional
import dotenv

# Handle imports for both package import and direct execution
try:
    from llm.generators.world_generator import WorldGenerator
except ImportError:
    # When running directly as a script
    import sys
    from pathlib import Path
    # Add the project root directory to sys.path
    project_root = str(Path(__file__).parent.parent.parent.absolute())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from llm.generators.world_generator import WorldGenerator


def setup_environment():
    """Load environment variables from .env file if it exists."""
    # First try to load from a .env file in the current directory
    if os.path.exists(".env"):
        dotenv.load_dotenv()
    
    # Also check for a .env file in the user's home directory
    home_env = os.path.join(os.path.expanduser("~"), ".airogue.env")
    if os.path.exists(home_env):
        dotenv.load_dotenv(home_env)


def generate_world(api_key: Optional[str] = None, output_path: Optional[str] = None, temperature: float = 1.0):
    """
    Generate a world and optionally save it to a file.
    
    Args:
        api_key: OpenAI API key. If None, will use OPENAI_API_KEY environment variable.
        output_path: Optional path to save the generated world as JSON.
        
    Returns:
        The generated WorldModel object.
    """
    generator = WorldGenerator(api_key=api_key, temperature=temperature)
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
        print(f"- {item.name} [{item.ascii_symbol}]: {item.description}")
    
    # Save to file if output path specified
    if output_path:
        with open(output_path, "w") as f:
            f.write(world.model_dump_json(indent=2))
        print(f"\nWorld saved to {output_path}")
    
    return world


def main():
    """Main entry point for the CLI."""
    # Load environment variables
    setup_environment()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate a roguelike game world")
    parser.add_argument("--api-key", type=str, help="OpenAI API key (if not provided, will use OPENAI_API_KEY env var)")
    parser.add_argument("--env-file", type=str, help="Path to .env file with OPENAI_API_KEY")
    parser.add_argument("--temperature", type=float, default=1.0, help="Temperature for LLM (default: 1.0)")
    parser.add_argument("--output", type=str, help="Output file path for the generated world (JSON format)")
    args = parser.parse_args()
    
    # Load from specific env file if provided
    if args.env_file and os.path.exists(args.env_file):
        dotenv.load_dotenv(args.env_file)
    
    # Get API key with precedence: command line > environment variable
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: No OpenAI API key provided. Use one of these methods:")
        print("1. Set the OPENAI_API_KEY environment variable")
        print("2. Create a .env file with OPENAI_API_KEY=your-key")
        print("3. Create a ~/.airogue.env file with OPENAI_API_KEY=your-key")
        print("4. Use the --api-key command line argument")
        print("5. Specify a custom .env file with --env-file")
        return 1
    
    # Generate the world
    try:
        generate_world(api_key, args.output, args.temperature)
        return 0
    except Exception as e:
        print(f"Error generating world: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
