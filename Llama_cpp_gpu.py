from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain_community.llms import LlamaCpp
import os
from langchain.prompts import PromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from kor.extraction import create_extraction_chain
from kor.nodes import Object, Text, Number
from pydantic import BaseModel, Field, conint, PositiveInt
from langchain_core.pydantic_v1 import BaseModel, Field, validator, conint, PositiveInt
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime
from langchain.output_parsers import RetryOutputParser,PydanticOutputParser
from langchain.schema import OutputParserException
import torch
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
from langchain.memory import ConversationBufferMemory
import json

class Position(str, Enum):
    top_right = "top-right"
    top_left = "top-left"
    center = "center"
    bottom_right = "bottom-right"
    bottom_left = "bottom-left"
    center_right = "center-right"
    center_top = "center-top"

class Structure(str, Enum):
    cannon = "cannon"
    mortar = "mortar"
    tower = "tower"
    headquarters = "headquarters"
    resource = "resource"

class Troops(str,Enum):
    shooters = "shooters"
    tanks = "tanks"
    helicopters = "helicopters"

class Defense(BaseModel):
    structure: Structure = Field(description="A defense structure type. Can have only one Headquarters.")
    position: Position = Field(description="Position of the defense structure.")

class ShooterLevels(BaseModel):
    health: PositiveInt = Field(description="Health of the shooter")
    damage: PositiveInt = Field(description="Damage of the shooter")
    speed: float = Field(description="Speed of the shooter")

class Shooters(BaseModel):
    noShooters: PositiveInt = Field(description="Number of shooters")

class TankLevels(BaseModel):
    health: PositiveInt = Field(description="Health of the tank")
    damage: PositiveInt = Field(description="Damage of the tank")

class Tanks(BaseModel):
    noTanks: PositiveInt = Field(description="Number of tanks")

class HelicopterLevels(BaseModel):
    health: PositiveInt = Field(description="Health of the helicopter")
    damage: PositiveInt = Field(description="Damage of the helicopter")

class Helicopters(BaseModel):
    noHelicopters: PositiveInt = Field(description="Number of helicopters")

class Environment(BaseModel):
    defenses: Dict[str, Defense] = Field(description="Dictionary of defenses. Keys of the dictionary will be like 'defense1','defense2' etc.")

class Agents(BaseModel):
    shooters: Shooters = Field(description="Details of shooters")
    tanks: Tanks = Field(description="Details of tanks")
    helicopters: Helicopters = Field(description="Details of helicopters")

class troopDeployment(BaseModel):
    troop: Troops = Field(description = "Type of agent deployed.")
    DeployedNumbers: PositiveInt = Field(description = "Number of agents deployed.")
    DeploymentPosition: Position = Field(description="Position of the agents deployed.")

class Deployment(BaseModel):
        deployments: Dict[str,troopDeployment] = Field(description = "Information about different types of agents deployed and their deployment positions. Keys will be like 'troop1','troop2' etc.")

class NodeType(str, Enum):
    sequence = "sequence"
    fallback = "fallback"

class LeafValues(str, Enum):
    check_tanks = "check_tanks?"
    check_helicopters = "check_helicopters?"
    check_health  = "check_health?"
    check_shooters = "check_shooters?"
    attack_towers = "attack_towers"
    attack_cannons = "attack_cannons"
    attack_mortars = "attack_mortars"
    check_towers = "check_towers?"
    check_cannons = "check_cannons?"
    check_mortar = "check_mortars?"
    check_resources = "check_resources?"
    attack_resources = "attack_resources"

class Node(BaseModel):
    node_type : NodeType = Field(description="A node can be either a type sequence, fallback. A sequence will visit each leaf node in order, starting with the first, and when that succeeds, will call the second, and so on down the list of leaf nodes until all the childrens returns Success or any one returns Failure. Fallback nodes execute leaf nodes in order from left to right until one returns Success or all return Failure.")
    leaf_values : List[LeafValues] = Field(description="Leaf values are the actions that the game will perform. The condition node (for example - check_towers?) will always come before the action nodes (for example - attack_resources).")

class BehaviorTree(BaseModel):
    nodes : List[Node] = Field(description="A behavior tree that defines the behavior of the agents.")

class target_priority(BaseModel):
    shooters: Structure = Field(description = "Specifies which structure shooters will attack first. Default is None.")
    tanks: Structure = Field(description = "Specifies which structure tanks will attack first. Default is None.")
    helicopters: Structure = Field(description = "Specifies which structure helicopters will attack first. Default is None.")

class GameConfig(BaseModel):
    environment: Environment = Field(description="Game environment configuration, responsible for running the game.")
    agents: Agents = Field(description="Details of agents.")
    deployment: Deployment = Field(description = "Deployment information about the agents.")
    behavior: target_priority = Field(description = "Defines the attacking behavior of the agents.")    

parser = PydanticOutputParser(pydantic_object=GameConfig)
schema = GameConfig.schema_json()

new_prompt = ChatPromptTemplate.from_messages(
    messages=[
       SystemMessage(
            content=f"<|im_start|>You are a helpful assistant that answers in JSON. Here's the json schema you must adhere to:\n<schema>\n{schema}\n</schema> <|im_end|>"
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(
            "<|im_start|>{human_input}<|im_end|>"
        ),  # Where the human input will injected
    ],
)

retry_prompt = PromptTemplate(
    template="<|im_start|>You are a helpful assistant that answers in JSON. Here's the json schema you must adhere to:\n<schema>\n{schema}\n</schema> <|im_end|> \n Human Message: {human_input}",
    input_variables=["human_input"],
    partial_variables={"schema": parser.get_format_instructions()},
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
llm = LlamaCpp(model_path = "/home/default/workspace/models/Hermes-2-Pro-Mistral-7B.Q8_0.gguf",
                n_gpu_layers = -1,
                n_batch = 1024,
                callback_manager = callback_manager,
                verbose = True,
               n_ctx = 3072,
               max_tokens = 3072,
               grammar_path = "/home/default/workspace/shield.gbnf",
              )
              
chat_llm_chain = LLMChain(
    llm=llm,
    prompt=new_prompt,
    verbose=True,
    memory=memory,
)

# query = "Generate a game configuration with six defenses. Of these six defenses, two are mortars placed at the center and center-right position. There are two towers at top-right and top-left corners. Also, two cannons are at the bottom-right and bottom-left positions. There are twenty agents available to us. Of these twenty, ten are shooters, five are tanks, and five are helicopters. I want to deploy five shooters from the top-right corner and five from the bottom-right corner. I want to deploy five tanks from the center-right and five helicopters from the bottom-left position. Helicopters will attack the towers first, tanks will attack the mortars first and shooters will attack the cannons first. "
# output = chat_llm_chain.predict(human_input = query)


def conversation_buff_llm(query):
    output = chat_llm_chain.predict(human_input = query['human_input'])
    try:
        parsed = parser.parse(output)
    except OutputParserException as e:
        retry_parser = RetryOutputParser.from_llm(parser = parser, llm = llm)
        prompt_value = retry_prompt.format_prompt(human_input = query)
        new_output = retry_parser.parse_with_prompt(output,prompt_value)
        output = new_output
    return output