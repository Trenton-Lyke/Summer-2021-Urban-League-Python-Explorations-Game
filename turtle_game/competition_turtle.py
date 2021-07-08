from __future__ import annotations
from math import sqrt, atan2, degrees
from queue import Queue
from threading import Lock, Barrier
from turtle import Turtle

from typing import Union, Callable, List, Tuple


from turtle_game.command import Command
from turtle_game.relative_location import RelativeLocation



class CompetitionTurtle:
    def __init__(self, team_name: str, is_prey: bool, color: Union[str,Tuple[float,float,float]], x: float, y: float, move_barrier: Barrier, check_barrier: Barrier,  process_queue: Queue, lock: Lock, __can_goto: Callable[[CompetitionTurtle],bool], __can_eat: Callable[[CompetitionTurtle,CompetitionTurtle],bool], predator_kill_radius: int, max_speed: float=10):
        self.__turtle: Turtle = Turtle()
        self.__turtle.shape('turtle')
        self.__team_name: str = team_name
        self.__turtle.speed("fastest")
        self.__turtle.color(color)
        self.__is_prey: bool = is_prey
        self.__turtle.shapesize(1 if self.__is_prey else 2)
        self.__turtle.penup()
        self.__move_barrier: Barrier = move_barrier
        self.__check_barrier: Barrier = check_barrier
        self.__process_queue: Queue = process_queue
        self.__lock: Lock = lock
        self.enemy_predators_relative_locations: List[RelativeLocation] = []
        self.enemy_prey_relative_locations: List[RelativeLocation] = []
        self.ally_predators_relative_locations: List[RelativeLocation] = []
        self.ally_prey_relative_locations: List[RelativeLocation] = []
        self.__energy: int = 5
        self.__started: bool = False
        self.__can_goto: Callable[[CompetitionTurtle],bool] = __can_goto
        self.__can_eat: Callable[[CompetitionTurtle, CompetitionTurtle], bool] = __can_eat
        self.predator_kill_radius = predator_kill_radius
        self.__waited = False
        self.__just_ate = False
        self.goto(x, y)
        self.__max_speed: float = max_speed

    def start(self):
        self.__started = True
    def is_prey(self) -> bool:
        return self.__is_prey

    def team_name(self) -> str:
        return self.__team_name

    def reset_wait(self):
        self.__waited = False


    def __add_to_queue(self, function: Callable[[float],None], value: float):
        self.__lock.acquire()
        self.__process_queue.put(Command(function, value))
        self.__lock.release()

    def wait(self, bonus=True):
        if bonus:
            self.__energy += 10
        else:
            self.__energy += 5
        self.__just_ate = False
        try:
            self.__move_barrier.wait()
        except Exception as e:
            print(e)
        try:
            self.__check_barrier.wait()
        except Exception as e:
            print(e)
        self.__waited = True

    def did_wait(self):
        return self.__waited
    def forward(self, speed: float):
        speed = min(speed, self.__energy, self.__max_speed)
        self.__energy -= speed
        self.__add_to_queue(self.__turtle.forward,speed)
        self.wait(False)

    def backward(self, speed: float):
        speed = min(speed, self.__energy, self.__max_speed)
        self.__energy -= speed
        self.__add_to_queue(self.__turtle.backward,speed)
        self.wait(False)

    def right(self, value: float):
        if self.__energy >= 1:
            self.__energy -= 1
            self.__add_to_queue(self.__turtle.right,value)
        self.wait(False)

    def left(self, value: float):
        if self.__energy >= 1:
            self.__energy -= 1
            self.__add_to_queue(self.__turtle.left,value)
        self.wait(False)

    def setheading(self, value: float):
        if self.__energy >= 1:
            self.__energy -= 1
            self.__add_to_queue(self.__turtle.setheading,value%360)
        self.wait(False)

    def position(self)->(float,float):
        return self.__turtle.position()

    def goto(self, x: float, y: float, ):
        if self.__can_goto(self):
            self.__turtle.goto(x,y)
        else:
            self.wait()

    def hide(self):
        self.__turtle.hideturtle()

    def eat(self, prey: CompetitionTurtle):
        if self.__can_eat(self,prey):
            self.__energy+=10
            self.__just_ate = True
    def did_just_eat(self):
        return self.__just_ate

    def distance(self, turtle2: CompetitionTurtle)->float:
        x1 = self.position()[0]
        y1 = self.position()[1]
        x2 = turtle2.position()[0]
        y2 = turtle2.position()[1]
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def angle(self, turtle2: CompetitionTurtle) -> float:
        x1 = self.position()[0]
        y1 = self.position()[1]
        x2 = turtle2.position()[0]
        y2 = turtle2.position()[1]
        return (degrees(atan2((y2 - y1), (x2 - x1))) + 360) % 360

    def energy_level(self):
        return self.__energy

    def closest_enemy_prey(self) -> RelativeLocation:
        if len(self.enemy_prey_relative_locations) > 0:
            return self.enemy_prey_relative_locations[0]
        else:
            return RelativeLocation(1,1)

    def closest_enemy_predator(self) -> RelativeLocation:
        if len(self.enemy_predators_relative_locations) > 0:
            return self.enemy_predators_relative_locations[0]
        else:
            return RelativeLocation(1, 1)

    def closest_ally_prey(self) -> RelativeLocation:
        if len(self.ally_prey_relative_locations) > 0:
            return self.ally_prey_relative_locations[0]
        else:
            return RelativeLocation(1, 1)

    def closest_ally_predator(self) -> RelativeLocation:
        if len(self.ally_predators_relative_locations) > 0:
            return self.ally_predators_relative_locations[0]
        else:
            return RelativeLocation(1, 1)



