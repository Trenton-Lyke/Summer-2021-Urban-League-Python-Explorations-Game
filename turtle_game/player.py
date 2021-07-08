from random import random
from typing import Union, Callable, Tuple

from turtle_game.competition_turtle import CompetitionTurtle
from turtle_game.world import World
from turtle_game.world_dimensions import WorldDimensions


class Player:
    def __init__(self, team_name: str, prey_color: Union[str,Tuple[float,float,float]] , predator_color: Union[str,Tuple[float,float,float]], prey_placement_function: Callable[[World, int],Tuple[float, float]], predator_placement_function: Callable[[World, int],Tuple[float, float]], prey_movement_function: Callable[[CompetitionTurtle,World], None], predator_movement_function: Callable[[CompetitionTurtle,World], None]):
        self.team_name: str = team_name
        self.prey_color: Union[str,Tuple[float,float,float]] = self.safe_color(prey_color)
        self.predator_color: Union[str,Tuple[float,float,float]] = self.safe_color(predator_color)
        self.prey_placement_function: Callable[[World, int], Tuple[float, float]] = prey_placement_function
        self.predator_placement_function: Callable[[World, int],Tuple[float, float]] = predator_placement_function
        self.prey_movement_function: Callable[[CompetitionTurtle, World], None] = prey_movement_function
        self.predator_movement_function: Callable[[CompetitionTurtle, World], None]= predator_movement_function

    def in_range(self, number: float, lower: float, upper: float):
        return number <= upper and number >= lower

    def safe_color(self, color: Union[str,Tuple[float,float,float]]):
        if isinstance(color, Tuple):
            if self.in_range(color[0],0,1) and self.in_range(color[1],0,1) and self.in_range(color[2],0,1):
                return color
            elif self.in_range(color[0],0,255) and self.in_range(color[1],0,255) and self.in_range(color[2],0,255):
                return (color[0]/255,color[1]/255,color[2]/255)
            else:
                return (random(),random(),random())
        else:
            return color