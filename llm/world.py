# llm/world.py
from providers.openai_provider import OpenAIProvider

class World:
    def __init__(self, setting):
        self.llm_provider = OpenAIProvider()
        self.setting = setting
        self.setting_details = ""
        # Initialize other attributes for the world generation
        # ...

    def generate_setting_details(self):
        prompt = f"Describe the key characteristics of a world with a {self.setting} setting. Include culture, history, and environment."
        self.setting_details = self.llm_provider.query(prompt, max_tokens=2000)
        return self.setting_details

    def generate_terrain(self):
        # Create a prompt specific to terrain generation
        terrain_prompt = f"Generate a detailed description of the terrain in a {self.setting} world."
        terrain_details = self.llm_provider.query(terrain_prompt)
        # Process terrain_details if necessary
        return terrain_details

    # Additional methods for other aspects of world generation
    # ...

    def generate_world(self):
        # This method orchestrates the calling of other methods to generate the full world
        self.generate_setting_details()
        # self.generate_terrain()
        self.generate_entity_categories()
        # ... generate other aspects

    def generate_entity_categories(self):
        prompt = (
            f"Given a roguelike game with a {self.setting} setting, "
            "list categories of entities that can be represented with symbols. "
            "Include creatures, items, NPCs, and terrain features."
        )
        categories_str = self.llm_provider.query(prompt, max_tokens=2000)
        # Process the response to split into categories
        self.entity_categories = [category.strip() for category in categories_str.split(',') if category.strip()]
        return self.entity_categories
    
# Usage example:
setting = "near future cyberpunk - neuroimplants, genetic modifications, corporation countries (Anclaves), neurohacking"
world_generator = World(setting)
world_details = world_generator.generate_world()
print(world_generator.setting_details)  # Print the setting details
print(world_generator.entity_categories)  # Print the setting details
# print(world_generator.setting_details)  # Print the setting details