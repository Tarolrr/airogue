# llm/world.py
import json
from pprint import pprint

# from providers.openai_provider import OpenAIProvider

class World:
    def __init__(self, setting):
        self.llm_provider = OpenAIProvider()
        self.setting = setting
        self.setting_details = ""
        # Initialize other attributes for the world generation
        # ...

    def generate_setting_details(self):
        system_prompt = f"Describe the key characteristics of a world for a roguelike game in a user-defined setting. Include culture, history, and environment."
        self.setting_details = self.llm_provider.query(system_prompt, self.setting, max_tokens=2000)
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
            "You're professional game designer. "
            "Your task is to come up with an exhaustive nested tree of categories of VALID entities for a roguelike game. "
            "You can decide if an entity is a VALID one if it follows the following rules: \n"
            "1. Have a specific size of not more than several meters. \n"
            "2. Can interact with another map entity in any way. \n"
            "3. Must have a defineable prcise spatial location. \n"
            "Example of a good category: Items->Weapons->Cold weapons\n"
            "Examples of a bad category:"
            "\tItems->Weapons->Cold weapons->Short sword - specific item listed\n"
            "\tCultural->Dance - does not have defined location\n"
            "\tLocation->Atomic station - a lot more than several meters in size\n"
            "Do not list specific entities in the leaf nodes. "
            "The leaf nodes should contain only a smallest sub-category along with it's description in the value. "
            "Only you as a game designer decide how nested each category should be. "
            "The setting of a game will be supplied by the user in the following message.\n"
            # "First, write a thousand word essay in plain text on how you would approach this complex and important task. "
            "Output ONLY a valid json with the following structure (your response as is will be read by a machine which accept only valid json):\n"
            '{"category": {"subcategory": {"subsubcategory": {"entity": "description"}}}}'
        )
        categories_str = self.llm_provider.query(prompt, self.setting_details, max_tokens=2000)
        # Process the response to split into categories
        try:
            self.entity_categories = json.loads(categories_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {categories_str}")
        return self.entity_categories

# Usage example:
# setting = "near future hard sci-fi world"
# world_generator = World(setting)
# world_details = world_generator.generate_world()
# print(world_generator.setting_details)  # Print the setting details
# pprint(world_generator.entity_categories)  # Print the setting details
# # print(world_generator.setting_details)  # Print the setting details
    
# from langchain.agents import AgentExecutor, AgentType, initialize_agent
# from langchain_core.agents import AgentFinish, AgentAction
# from langchain.agents.output_parsers import SelfAskOutputParser
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_community.tools.
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are very powerful assistant, but don't know current events",
#         ),
#         ("user", "{input}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad"),
#     ]
# )


# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# list(agent_executor.stream({"input": "Hi"}))
    
from langchain.agents import Agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.output_parsers import SelfAskOutputParser
from langchain.agents.chat.output_parser import ChatOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.agents import AgentFinish, AgentAction
from langchain.agents.chat.base import BasePromptTemplate
from langchain.chains.llm import LLMChain


# class ReasoningAgent(Agent):
#     def __init__(self, llm, prompt_template):
#         llm_chain = LLMChain(
#             llm=llm,
#             prompt=prompt_template,
#             # ... possibly other parameters ...
#         )        
#         output_parser = SelfAskOutputParser()

#         super().__init__(llm_chain=llm_chain, output_parser=output_parser)
#         self.llm = llm
#         self.prompt_template = prompt_template

#     def invoke(self, question):
#         return self.generate_and_check_answer(question)
    
#     # Implementing abstract methods
#     @classmethod
#     def _get_default_output_parser(cls, **kwargs):
#         return ChatOutputParser()
    
#     @classmethod
#     def create_prompt(cls, tools, system_message_prefix, system_message_suffix, human_message, format_instructions, input_variables=None, **kwargs):
#         return BasePromptTemplate()
    
#     @property
#     def llm_prefix(self):
#         return "Thought:"
    
#     @property
#     def observation_prefix(self):
#         return "Observation: "

#     def generate_and_check_answer(self, question):
#         reasoning_prompt = self.prompt_template.format(
#             question=question,
#             previous_steps=""
#         )
        
#         # Generate an initial answer
#         initial_answer = self.llm.query(reasoning_prompt)
        
#         # Check the answer
#         check_prompt = self.prompt_template.format(
#             question=f"Verify the following information: {initial_answer}",
#             previous_steps=reasoning_prompt + "\n" + initial_answer
#         )
#         check_result = self.llm.query(check_prompt)
        
#         # Decide if the answer is good enough or needs regeneration
#         if "correct" in check_result.lower():
#             return initial_answer
#         else:
#             # Regenerate the answer if needed
#             return self.generate_and_check_answer(question)
    
#     def invoke(self, question):
#         return self.generate_and_check_answer(question)

# # Initialize the language model
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# # Create a prompt template for reasoning and checking
# prompt_template = ChatPromptTemplate.from_messages([
#     ("system", "You are a helpful assistant capable of independent reasoning. Generate an answer to the question and then verify its correctness."),
#     ("user", "{question}"),
#     ("system", "{previous_steps}"),
#     MessagesPlaceholder(variable_name="agent_scratchpad"),
# ])

# # Create an instance of the ReasoningAgent
# reasoning_agent = ReasoningAgent(llm, prompt_template)

# # Example usage
# agent_executor = AgentExecutor(agent=reasoning_agent, tools=[])
# question = "What is the capital of France?"
# answer = agent_executor.invoke({"input": question})
# print(answer)

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


from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=1.7)
from langchain.agents import tool


@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

tool_mem = []
@tool
def game_designer_assistant(input: str) -> str:
    """Helps in various questions related to game design."""
    tool_mem.append(("user", input))
    _prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a game designer assistant. You can help me design games."),
        ] + tool_mem
    )
    _llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tool_mem.append(("assistant", LLMChain(llm=_llm, prompt=_prompt).invoke({"input": input})["text"]))
    return tool_mem[-1][1]

tools = [game_designer_assistant]
# print(game_designer_assistant.invoke("abc"))
# exit(0)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are very powerful assistant",
        ),
            ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
# llm_with_tools = llm.bind_tools(tools)

from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm
    | OpenAIToolsAgentOutputParser()
)
import yaml
# print(yaml.safe_dump(agent.output_schema.schema()))


from langchain.agents import AgentExecutor
print(type(agent))
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# list(agent_executor.stream({"input": "Imagine 2d ascii game. Try to come up with a `screenshot` of it based on what you know about such kind of games. Theme does not matter. You also should imagine one. Try to think through how would you do it"}))
print(list(agent_executor.batch([{"input": "Come up with a title for a game. Avoid the words 'realm' and 'legends' and colon sign"}]*20)))
# list(agent_executor.stream({"input": "I want to generate a list of categories of game items for a roguelike game in fantasy setting. "
#                                      "You need to follow the process:"
#                                      "\n - generate a list"
#                                      "\n - write a constructive feedback to improve it and send it alogn with the list to the tool again"
#                                      "\n - return the result to me"}))
# print(agent.invoke(input={"input": "How many letters in the word eudca", "intermediate_steps": []}))