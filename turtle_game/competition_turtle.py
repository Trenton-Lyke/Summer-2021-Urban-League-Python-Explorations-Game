from __future__ import annotations
from math import sqrt, atan2, degrees
from queue import Queue
from threading import Lock, Barrier
from turtle import Turtle

from typing import Union, Callable, List, Tuple


from turtle_game.command import Command
from turtle_game.relative_location import RelativeLocation



class CompetitionTurtle:
    def __init__(self, team_name: str, is_prey: bool, color: Union[str,Tuple[float,float,float]], x: float, y: float, move_barrier: Barrier, check_barrier: Barrier, process_queue: Queue, lock: Lock, can_move_without_wait: Callable[[CompetitionTurtle], bool], can_eat: Callable[[CompetitionTurtle, CompetitionTurtle], bool], is_game_over: Callable[[], bool], is_turtle_on_left_edge: Callable[[CompetitionTurtle], bool], is_turtle_on_top_edge: Callable[[CompetitionTurtle], bool], is_turtle_on_right_edge: Callable[[CompetitionTurtle], bool], is_turtle_on_bottom_edge: Callable[[CompetitionTurtle], bool], is_turtle_in_top_left_corner: Callable[[CompetitionTurtle], bool], is_turtle_in_top_right_corner: Callable[[CompetitionTurtle], bool], is_turtle_in_bottom_right_corner: Callable[[CompetitionTurtle], bool], is_turtle_in_bottom_left_corner: Callable[[CompetitionTurtle], bool], max_speed: float):
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
        self.__can_move_without_wait: Callable[[CompetitionTurtle], bool] = can_move_without_wait
        self.__can_eat: Callable[[CompetitionTurtle, CompetitionTurtle], bool] = can_eat
        self.__waited = False
        self.__just_ate = False
        self.__is_alive = True
        self.goto(x, y)
        self.__max_speed: float = max_speed
        self.__is_game_over: Callable[[],bool] = is_game_over
        self.__is_turtle_on_left_edge: Callable[[CompetitionTurtle],bool] = is_turtle_on_left_edge
        self.__is_turtle_on_top_edge: Callable[[CompetitionTurtle],bool] = is_turtle_on_top_edge
        self.__is_turtle_on_right_edge: Callable[[CompetitionTurtle],bool] = is_turtle_on_right_edge
        self.__is_turtle_on_bottom_edge: Callable[[CompetitionTurtle],bool] = is_turtle_on_bottom_edge
        self.__is_turtle_in_top_left_corner: Callable[[CompetitionTurtle],bool] = is_turtle_in_top_left_corner
        self.__is_turtle_in_top_right_corner: Callable[[CompetitionTurtle],bool] = is_turtle_in_top_right_corner
        self.__is_turtle_in_bottom_right_corner: Callable[[CompetitionTurtle],bool] = is_turtle_in_bottom_right_corner
        self.__is_turtle_in_bottom_left_corner: Callable[[CompetitionTurtle],bool] = is_turtle_in_bottom_left_corner

    def start(self):
        self.__started = True
    def is_prey(self) -> bool:
        return self.__is_prey

    def team_name(self) -> str:
        return self.__team_name

    def reset_wait(self):
        self.__waited = False


    def __add_to_queue(self, function: Callable[[float],None], value: float):
        if self.__is_alive:
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
        if self.__is_alive:
            speed = min(speed, self.__energy, self.__max_speed)
            self.__energy -= speed
            self.__add_to_queue(self.__turtle.forward,speed)
        self.wait(False)

    def backward(self, speed: float):
        if self.__is_alive:
            speed = min(speed, self.__energy, self.__max_speed)
            self.__energy -= speed
            self.__add_to_queue(self.__turtle.backward,speed)
        self.wait(False)

    def right(self, value: float):
        if self.__is_alive:
            if self.__energy >= 1:
                self.__energy -= 1
                self.__add_to_queue(self.__turtle.right,value)
        self.wait(False)

    def left(self, value: float):
        if self.__is_alive:
            if self.__energy >= 1:
                self.__energy -= 1
                self.__add_to_queue(self.__turtle.left,value)
        self.wait(False)

    def setheading(self, value: float):
        if self.__is_alive:
            if self.__energy >= 1:
                self.__energy -= 1
                self.__add_to_queue(self.__turtle.setheading,value%360)
        self.wait(False)

    def position(self)->(float,float):
        return self.__turtle.position()

    def goto(self, x: float, y: float, ):
        if self.__can_move_without_wait(self):
            try:
                self.__turtle.goto(x,y)
            except:
                pass
        else:
            self.wait()

    def force_heading(self, angle: float):
        if self.__can_move_without_wait(self):
            try:
                self.__turtle.setheading(angle)
            except:
                pass
        else:
            self.wait()
    def hide(self):
        self.__turtle.hideturtle()
        self.__is_alive = False

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

    def angle_to_closest_enemy_prey(self) -> float:
        return self.closest_enemy_prey().angle()

    def distance_to_closest_enemy_prey(self) -> float:
        return self.closest_enemy_prey().distance()

    def closest_enemy_predator(self) -> RelativeLocation:
        if len(self.enemy_predators_relative_locations) > 0:
            return self.enemy_predators_relative_locations[0]
        else:
            return RelativeLocation(1, 1)

    def angle_to_closest_enemy_predator(self) -> float:
        return self.closest_enemy_predator().angle()

    def distance_to_closest_enemy_predator(self) -> float:
        return self.closest_enemy_predator().distance()

    def closest_ally_prey(self) -> RelativeLocation:
        if len(self.ally_prey_relative_locations) > 0:
            return self.ally_prey_relative_locations[0]
        else:
            return RelativeLocation(1, 1)

    def angle_to_closest_ally_prey(self) -> float:
        return self.closest_ally_prey().angle()

    def distance_to_closest_ally_prey(self) -> float:
        return self.closest_ally_prey().distance()

    def closest_ally_predator(self) -> RelativeLocation:
        if len(self.ally_predators_relative_locations) > 0:
            return self.ally_predators_relative_locations[0]
        else:
            return RelativeLocation(1, 1)

    def angle_to_closest_ally_predator(self) -> float:
        return self.closest_ally_predator().angle()

    def distance_to_closest_ally_predator(self) -> float:
        return self.closest_ally_predator().distance()

    def turn_to_closest_enemy_prey(self):
        self.setheading(self.angle_to_closest_enemy_prey())

    def turn_to_closest_enemy_predator(self):
        self.setheading(self.angle_to_closest_enemy_predator())

    def turn_to_closest_ally_prey(self):
        self.setheading(self.angle_to_closest_ally_prey())

    def turn_to_closest_ally_predator(self):
        self.setheading(self.angle_to_closest_ally_predator())

    def turn_away_from_closest_enemy_prey(self):
        self.setheading(self.angle_to_closest_enemy_prey()+180)

    def turn_away_from_enemy_predator(self):
        self.setheading(self.angle_to_closest_enemy_predator()+180)

    def turn_away_from_closest_ally_prey(self):
        self.setheading(self.angle_to_closest_ally_prey()+180)

    def turn_away_from_closest_ally_predator(self):
        self.setheading(self.angle_to_closest_ally_predator()+180)

    def max_speed(self) -> float:
        return self.__max_speed

    def is_turtle_on_left_edge(self) -> bool:
        return self.__is_turtle_on_left_edge(self)
    def is_turtle_on_top_edge(self) -> bool:
        return self.__is_turtle_on_top_edge(self)
    def is_turtle_on_right_edge(self) -> bool:
        return self.__is_turtle_on_right_edge(self)
    def is_turtle_on_bottom_edge(self) -> bool:
        return self.__is_turtle_on_bottom_edge(self)
    def is_turtle_in_top_left_corner(self) -> bool:
        return self.__is_turtle_in_top_left_corner(self)
    def is_turtle_in_top_right_corner(self) -> bool:
        return self.__is_turtle_in_top_right_corner(self)
    def is_turtle_in_bottom_right_corner(self) -> bool:
        return self.__is_turtle_in_bottom_right_corner(self)
    def is_turtle_in_bottom_left_corner(self) -> bool:
        return self.__is_turtle_in_bottom_left_corner(self)
    def heading(self) -> float:
        return self.__turtle.heading()
