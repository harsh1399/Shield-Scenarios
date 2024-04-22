from pydantic import BaseModel, Field, conint, PositiveInt
from enum import Enum
from typing import List, Dict, Optional
from langchain.output_parsers import PydanticOutputParser

class Position(str, Enum):
    top_right = "top right"
    top_left = "top left"
    center = "center"
    bottom_right = "bottom right"
    bottom_left = "bottom left"
    center_right = "center right"
    center_top = "center top"

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
    structure: Structure = Field(description="A defense structure type, each have their advantages. Can have only one Headquarters")
    position: Position = Field(description="Position of the defense structure, each position can not be too crowded.")
    # level: PositiveInt = Field(description="Level of the defense")
    # shotSpeed: Optional[conint(ge=1)] = Field(None, description="Speed of shots (if applicable)")
    # hitpoint: Optional[PositiveInt] = Field(None, description="Hitpoints of the defense")
    # damage: Optional[PositiveInt] = Field(None, description="Damage caused by the defense")

class ShooterLevels(BaseModel):
    health: PositiveInt = Field(description="Health of the shooter")
    damage: PositiveInt = Field(description="Damage of the shooter")
    speed: float = Field(description="Speed of the shooter")

class Shooters(BaseModel):
    noShooters: PositiveInt = Field(description="Number of shooters")
    # shooterMaxLevel: PositiveInt = Field(description="Maximum level of shooters")
    # levels: Dict[str, ShooterLevels] = Field(description="Levels of shooters")

class TankLevels(BaseModel):
    health: PositiveInt = Field(description="Health of the tank")
    damage: PositiveInt = Field(description="Damage of the tank")

class Tanks(BaseModel):
    noTanks: PositiveInt = Field(description="Number of tanks")
    # tanksMaxLevel: PositiveInt = Field(description="Maximum level of tanks")
    # levels: Dict[str, TankLevels] = Field(description="Levels of tanks")

class HelicopterLevels(BaseModel):
    health: PositiveInt = Field(description="Health of the helicopter")
    damage: PositiveInt = Field(description="Damage of the helicopter")

class Helicopters(BaseModel):
    noHelicopters: PositiveInt = Field(description="Number of helicopters")
    # shooterMaxLevel: PositiveInt = Field(description="Maximum level of helicopters")
    # levels: Dict[str, HelicopterLevels] = Field(description="Levels of helicopters")

class Environment(BaseModel):
    defenses: Dict[str, Defense] = Field(description="Dictionary of defenses")

class Agents(BaseModel):
    shooters: Shooters = Field(description="Details of shooters")
    tanks: Tanks = Field(description="Details of tanks")
    helicopters: Helicopters = Field(description="Details of helicopters")

class troopDeployment(BaseModel):
    troop: Troops = Field(description = "Type of agent deployed.")
    DeployedNumbers: PositiveInt = Field(description = "Number of agents deployed.")
    DeploymentPosition: Position = Field(description="Position of the agents deployed.")

class Deployment(BaseModel):
        deployments: Dict[str,troopDeployment] = Field(description = "Information about different types of agents deployed and their deployment positions.")

class GameConfig(BaseModel):
    environment: Environment = Field(description="Game environment configuration, responsible for running the game.")
    agents: Agents = Field(description="Details of agents.")
    deployment: Deployment = Field(description = "Deployment information about the agents.")

parser = PydanticOutputParser(pydantic_object=GameConfig)
