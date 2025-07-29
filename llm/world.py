import random
from operator import itemgetter

from colored import attr, fg
# from langchain.agents import Agent, AgentExecutor
# from langchain.agents.chat.base import BasePromptTemplate
# from langchain.agents.chat.output_parser import ChatOutputParser
# from langchain.agents.output_parsers import SelfAskOutputParser

from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
# from langchain.chains.llm import LLMChain
# from langchain_core.agents import AgentFinish, AgentAction
from langchain_core.output_parsers import JsonOutputParser, NumberedListOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.runnables.passthrough import identity
from langchain_openai import ChatOpenAI
from models import GameMechanics, Items, Themes, WorldModel
# import logging
# logging.getLogger("langchain").setLevel(logging.DEBUG)
# logging.getLogger("httpcore").setLevel(logging.INFO)
# logging.getLogger("httpx").setLevel(logging.INFO)
# import sys
# logging.basicConfig(
#     format="%(asctime)s %(levelname)s %(name)s %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     level=logging.DEBUG,
#     stream=sys.stdout,
# )


class SelectRandomOutputParser(JsonOutputParser):
    def parse_result(self, text: str) -> str:
        list_ = super().parse_result(text)["themes"]
        return random.choice(list_)


theme_parser = SelectRandomOutputParser(pydantic_object=Themes)
item_parser = OutputFixingParser(parser=PydanticOutputParser(pydantic_object=Items), llm=ChatOpenAI)
gm_parser = OutputFixingParser(parser=PydanticOutputParser(pydantic_object=GameMechanics), llm=ChatOpenAI)


class World:
    def __init__(self, setting):
        self.setting = setting
        self.setting_details = ""
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=1)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", 
                    "You are professional game designer."
                    "You're very creative and always trying to come up with unique solutions."
                    "Avoid using cliche, game design stereotypes and expected solutions."
                    "There are certain requirements that you should keep in mind at all times while designing the game:\n"
                    "1. The genre is roguelike, singleplayer, minimalistic.\n"
                    "2. The game uses 2D ASCII engine.\n"
                    "3. The game engine does not support sound.\n"
                    "4. The game is terminal-only (engine supports drawing environment with different symbols).\n"
                    "5. The game experience should be short. No more than an hour."),
                ("user", "{input}"),

            ]
        )
        self.chain = (
            {
                "input": lambda x: x["input"]
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        self.partial_chain = (
            {
                "input": lambda x: x["input"]
            }
            | self.prompt
            | self.llm
        )
        self.design_doc = ""

    def theme(self):
        themes_prompt = {
            "input": (
                f"Generate different, \"orthogonal\" themes for a game."
                f"\n{theme_parser.get_format_instructions()}"
            )
        }
        chain = self.partial_chain | theme_parser
        theme = chain.invoke(themes_prompt)
        return theme

    def generate_title(self, theme):
        title_prompt = {
            "input": f"Generate a title for a game with the following theme {theme}."
        }

        title = self.chain.invoke(title_prompt)
        self.design_doc += f"Theme: {theme}\n"
        self.design_doc += f"Title: {title}\n"
        return title

    def generate_plot(self, theme, title):
        plot_prompt = {
            "input": (
                f"Generate a plot for a game with title {title} and the following overall theme: {theme}."
            )
        }
        plot = self.chain.invoke(plot_prompt)
        self.design_doc += f"Plot: {plot}\n"
        return plot

    def generate_game_mechanics(self, theme, title, plot):
        game_mechanics_prompt = {
            "input": (
                f"Generate detailed game mechanics for a minimalistic console game with a title {title} and the following overall theme: {theme}. "
                f"Main writer already wrote the plot for the game. "
                f"Make sure that the game mechanics are strictly aligned with it. "
                f"Make sure that the game mechanics are clear, concrete and specific.\n"
                f"Here's the plot:\n{plot}\n"
                f"\n{gm_parser.get_format_instructions()}"
            )
        }
        chain = self.partial_chain | gm_parser
        return chain.invoke(game_mechanics_prompt).mechanics

    def generate_items(self, game_mechanic):
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
                f"{item_parser.get_format_instructions()}"
            )
        }

        chain = self.partial_chain | item_parser
        return chain.invoke(items_prompt).items

    def generate_world(self):
        themes_prompt = {
            "input": lambda x: (
                f"Generate different, \"orthogonal\" themes for a game."
                f"\n{theme_parser.get_format_instructions()}"
            )
        }

        title_prompt = {
            "input": "Generate a title for a game with the following theme {theme}."
        }

        plot_prompt = {
            "input3": (
                "Generate a plot for a game with title {title} and the following overall theme: {theme}."
            )
        }

        game_mechanics_prompt = {
            "input4": (
                "Generate detailed game mechanics for a minimalistic console game with a title {title} and the following overall theme: {theme}. "
                "Main writer already wrote the plot for the game. "
                "Make sure that the game mechanics are strictly aligned with it. "
                "Make sure that the game mechanics are clear, concrete and specific.\n"
                "Here's the plot:\n{plot}\n"
                # f"\n{gm_parser.get_format_instructions()}"
            )
        }

        items_prompt = {
            "input": (
                "We're in the process of a game design. "
                "You will be supplied with the design document and one of the game mechanics. "
                "Your job is to come up with a list of 10 items that will be used in the game. "
                "They should be strictly aligned with the game mechanics given. "
                "If the game mechanic does not have anything to do with the items, give an empty list.\n"
                "Here's the design document:\n"
                "Theme: {theme}\n"
                "Title: {title}\n"
                "Plot: {plot}\n\n"
                "Here are the game mechanics:\n"
                "{mechanics}\n"
                # f"\n{item_parser.get_format_instructions()}"
            )
        }

        chain = (
            themes_prompt | self.prompt | self.llm | theme_parser
            | RunnableParallel(
                theme=identity,
                title={"input": lambda x: title_prompt["input"].format(theme=x)} | self.prompt | self.llm | StrOutputParser(),
            )
            | RunnableParallel(
                theme=itemgetter("theme"),
                title=itemgetter("title"),
                plot={"input": lambda x: plot_prompt["input3"].format(**x)} | self.prompt | self.llm | StrOutputParser(),
            )
            | RunnableParallel(
                theme=itemgetter("theme"),
                title=itemgetter("title"),
                plot=itemgetter("plot"),
                mechanics={"input": lambda x: game_mechanics_prompt["input4"].format(**x) + "\n" + gm_parser.get_format_instructions()} | self.prompt | self.llm | gm_parser,
            )
            | RunnableParallel(
                theme=itemgetter("theme"),
                title=itemgetter("title"),
                plot=itemgetter("plot"),
                mechanics=itemgetter("mechanics"),
                items={"input": lambda x: items_prompt["input"].format(**(x | {"mechanics": str(x["mechanics"])})) + "\n" + item_parser.get_format_instructions()} | self.prompt | self.llm | item_parser,
            )
        )
        return WorldModel(**chain.invoke(None))

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

if __name__ == "__main__":
    world = World(None)
    # from langchain_core.output_parsers import ListOutputParser
    # print(ListOutputParser().parse('["a", "b", "c"]'))
    # exit(0)
    from langchain_core.runnables import RunnablePassthrough, RunnableParallel
    name_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Return a single name and surname pair. Nothing else"),
        ]
    )
    
    job_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Write {name} in cyrillic. Nothing else"),
        ]
    )

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=1)
    chain1 = (
        {} 
        | name_prompt
        | llm
        | StrOutputParser()

    )
    # name = chain1.invoke(None)
    # print(name)
    chain2 = (
        chain1
        | RunnableParallel(
            name=RunnablePassthrough(),
            job={"name": lambda x: x} | job_prompt | llm | StrOutputParser()
        )
        | (lambda x: f"{x['name']} - {x['job']}")
    )

    # job = chain2.invoke({"name": name})
    # job = chain2.invoke(None)
    # print(job)
    # exit(0)
    import json
    with open('../world_model.json', 'r') as f:
        world_model = WorldModel(**json.load(f))

    # world_model = world.generate_world()
    # print(world_model)
    # with open('world_model.json', 'w') as f:
    #     f.write(world_model.json())
    # exit(0)
    theme = world.theme()
    print(theme)
    title = world.generate_title(theme)
    print(title)
    plot = world.generate_plot(theme, title)
    print(plot)
    game_mechanics = world.generate_game_mechanics(theme, title, plot)
    print(game_mechanics)
    exit(0)
    total_items = []
    for line in game_mechanics:
        items = world.generate_items(line)
        total_items += items

    world.print_world(theme, title, plot, game_mechanics, total_items)
