from random import random
from turtle import screensize, Screen
from typing import List, Tuple

from turtle_game.competition_turtle import CompetitionTurtle
from turtle_game.world_dimensions import WorldDimensions


class World:
    def __init__(self, width: int=700, height: int=700, predator_kill_radius: int =30, background=True):
        self.world_dimensions: WorldDimensions = WorldDimensions(width,height)
        self.turtles: List[CompetitionTurtle] = []
        self.prey: List[CompetitionTurtle] = []
        self.predators: List[CompetitionTurtle] = []
        self.__predator_kill_radius: int = predator_kill_radius
        screensize(int(self.world_dimensions.width()), int(self.world_dimensions.height()))
        Screen().clear()
        if background:
            Screen().bgpic("background.png")

    def is_in_bounds(self, turtle: CompetitionTurtle):
        x=turtle.position()[0]
        y=turtle.position()[1]
        return x > self.world_dimensions.min_x() and x < self.world_dimensions.max_x() and y > self.world_dimensions.min_y() and y < self.world_dimensions.max_y()

    def random_location(self) -> Tuple[float,float]:
        x:float=(random()-.5)*(self.world_dimensions.max_x() - self.world_dimensions.min_x())
        y:float=(random()-.5)*(self.world_dimensions.max_y() - self.world_dimensions.min_y())
        return (x,y)

    def predator_kill_radius(self) -> int:
        return self.__predator_kill_radius







