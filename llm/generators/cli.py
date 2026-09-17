#!/usr/bin/env python
"""
Command-line interface for the world generator.
This script allows the world generator to be run as a standalone tool.
"""
import os
import sys
import json
import argparse
import shutil
from typing import Optional
try:
    import dotenv
except ImportError:  # python-dotenv is not a direct project dependency.
    dotenv = None

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


def load_environment_file(path: str) -> None:
    """Load a simple ``KEY=VALUE`` environment file without extra packages."""
    if dotenv is not None:
        dotenv.load_dotenv(path)
        return

    with open(path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def setup_environment():
    """Load environment variables from .env file if it exists."""
    # First try to load from a .env file in the current directory
    if os.path.exists(".env"):
        load_environment_file(".env")
    
    # Also check for a .env file in the user's home directory
    home_env = os.path.join(os.path.expanduser("~"), ".airogue.env")
    if os.path.exists(home_env):
        load_environment_file(home_env)


def generate_world(api_key: Optional[str] = None, output_path: Optional[str] = None, temperature: float = 1.0,
                   provider: str = "openai", codex_command: str = "codex",
                   codex_timeout: float = 60.0):
    """
    Generate a world and optionally save it to a file.
    
    Args:
        api_key: OpenAI API key. If None, will use OPENAI_API_KEY environment variable.
        output_path: Optional path to save the generated world as JSON.
        
    Returns:
        The generated WorldModel object.
    """
    generator = WorldGenerator(api_key=api_key, temperature=temperature, provider=provider,
                               codex_command=codex_command, codex_timeout=codex_timeout)
    try:
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
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(world.model_dump_json(indent=2))
            print(f"\nWorld saved to {output_path}")
        return world
    finally:
        generator.close()


def main():
    """Main entry point for the CLI."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate a roguelike game world")
    parser.add_argument("--provider", choices=("openai", "codex"), default="openai",
                        help="Generation backend (default: openai)")
    parser.add_argument("--api-key", type=str, help="OpenAI API key (if not provided, will use OPENAI_API_KEY env var)")
    parser.add_argument("--env-file", type=str, help="Path to .env file with OPENAI_API_KEY")
    parser.add_argument("--temperature", type=float, default=1.0, help="Temperature for LLM (default: 1.0)")
    parser.add_argument("--output", type=str, help="Output file path for the generated world (JSON format)")
    parser.add_argument("--codex-command", default="codex", help="Local Codex executable (default: codex)")
    parser.add_argument("--codex-timeout", type=float, default=60.0,
                        help="Seconds to wait for Codex App Server (default: 60)")
    args = parser.parse_args()
    
    api_key = None
    if args.provider == "openai":
        setup_environment()
        # Load from specific env file if provided
        if args.env_file and os.path.exists(args.env_file):
            load_environment_file(args.env_file)
        # Command line has precedence over the configured environment.
        api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    
    if args.provider == "openai" and not api_key:
        print("Error: No OpenAI API key provided. Use one of these methods:")
        print("1. Set the OPENAI_API_KEY environment variable")
        print("2. Create a .env file with OPENAI_API_KEY=your-key")
        print("3. Create a ~/.airogue.env file with OPENAI_API_KEY=your-key")
        print("4. Use the --api-key command line argument")
        print("5. Specify a custom .env file with --env-file")
        return 1
    if args.provider == "codex" and not (shutil.which(args.codex_command) or
                                          (os.path.isabs(args.codex_command) and os.access(args.codex_command, os.X_OK))):
        print("Error: Codex CLI is unavailable. Install Codex and complete `codex login` on this trusted local machine.")
        return 1
    
    # Generate the world
    try:
        generate_world(api_key=api_key, output_path=args.output, temperature=args.temperature,
                       provider=args.provider, codex_command=args.codex_command,
                       codex_timeout=args.codex_timeout)
        return 0
    except Exception as e:
        print(f"Error generating world: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
