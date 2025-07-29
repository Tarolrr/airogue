from typing import Any, Dict, List, Union

from colored import attr, fg

from langchain_core.pydantic_v1 import BaseModel, Field


class Item(BaseModel):
    name: str
    ascii_symbol: str = Field(description="A single ASCII character representing the item")
    description: str

    def __str__(self):
        return f"[{self.ascii_symbol}] {self.name}: {self.description}"


class Items(BaseModel):
    items: List[Item]

    def to_string(self, enable_formatting=True):
        def fmt(s):
            if enable_formatting:
                return fg("green") + attr("bold") + s + attr("reset")
            else:
                return s
        return fmt("- ") + fmt("\n- ").join([str(i) for i in self.items])
    
    def __str__(self):
        return self.to_string(enable_formatting=False)


class GameMechanic(BaseModel):
    name: str
    description: str

    def __str__(self):
        return f"{self.name}: {self.description}"


class GameMechanics(BaseModel):
    mechanics: List[GameMechanic]

    def __str__(self):
        return "- " + "\n- ".join(self.mechanics)


class Themes(BaseModel):
    themes: List[str] = Field(min_items=10, max_items=10)


class Action(BaseModel):
    name: str
    description: str
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.function = get_action_function(name)

    def execute(self):
        # Execute the corresponding function from slots.py
        self.function(**self.args)

class Pipeline(BaseModel):
    def __init__(self, actions):
        self.actions = actions  # List of Action objects

    def trigger(self):
        for action in self.actions:
            action.execute()


class ComponentModel(BaseModel):
    name: str
    attributes: Dict[str, Any] = {}
    pipelines: List[Action] = []


class EntityModel(BaseModel):
    name: str
    uid: Union[str, int, object] = Field(default_factory=object)
    components: List[ComponentModel] = []



class WorldModel(BaseModel):
    theme: str
    title: str
    plot: str
    mechanics: GameMechanics
    items: Items
    global_entities: List[EntityModel] = []

    def to_string(self, enable_formatting=True):
        def fmt(s):
            if enable_formatting:
                return fg("green") + attr("bold") + s + attr("reset")
            else:
                return s

        ret  = fmt("Theme: ") + self.theme + "\n\n"
        ret += fmt("Title: ") + self.title + "\n\n"
        ret += fmt("Plot: ") + self.plot  + "\n\n"

        ret += fmt("Game mechanics:\n")
        for line in self.mechanics.mechanics:
            ret += fmt("- ") + str(line) + "\n"

        ret += fmt("Items:\n")
        ret += self.items.to_string(enable_formatting=enable_formatting)

        return ret

    def __str__(self) -> str:
        return self.to_string(enable_formatting=False)
    
    def print(self):
        print(self.to_string(enable_formatting=True))
