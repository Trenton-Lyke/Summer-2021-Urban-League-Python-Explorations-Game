import sys
from importlib import import_module
import os
from queue import Queue
from random import random, randint
from threading import Barrier, Lock
from typing import Union, Tuple, Callable

from turtle_game.competition_turtle import CompetitionTurtle
from turtle_game.match import run_match
import turtle_programs
from turtle_game.player import Player
from turtle_game.stoppable_thread import StoppableThread
from turtle_game.world import World
from turtle_game.world_dimensions import WorldDimensions


def check_color_tuple(color_tuple):
    valid = True
    for val in color_tuple:
        valid &= isinstance(val,float)
    return valid
def default_placement_function(world: World, prey_number: int) -> Tuple[float, float]:
    return world.random_location()

def default_movement_function(turtle: CompetitionTurtle, world: World):
    num = randint(0,4)
    if num == 0:
        turtle.right(30)
    elif num == 1:
        turtle.left(30)
    elif num == 2:
        turtle.forward(3)
    elif num == 3:
        turtle.backward(3)
    else:
        turtle.wait()

def test_function(function, *arguments):
    try:
        function(*arguments)
    except:
        pass
def test_function_time(time: float, function: Callable, *arguments):
    for i in range(100):
        try:
            test_thred = StoppableThread(target=test_function, args=(function,*arguments,))
            test_thred.start()
            test_thred.join(time)
            if test_thred.is_alive():
                test_thred.stop()
                return False
        except:
            pass
    return True

def can_goto( turtle: CompetitionTurtle):
    return False
def can_eat(prey: CompetitionTurtle):
    return False if randint(0,1)==1 else True

def failsafes(person):
    team_name: str
    prey_color: Union[str,Tuple[float,float,float]]
    predator_color: Union[str,Tuple[float,float,float]]
    prey_placement_function: Callable[[World, int],Tuple[float, float]]
    predator_placement_function: Callable[[World, int],Tuple[float, float]]
    prey_movement_function: Callable[[CompetitionTurtle, World], None]
    predator_movement_function: Callable[[CompetitionTurtle, World], None]
    if not hasattr(person,"team_name") or not isinstance(person.team_name,str):
        print("Team name falesafe triggered")
        team_name = "Untitled Team"
    else:
        team_name = person.team_name
    if not (hasattr(person,"prey_color")  and (isinstance(person.prey_color, str) or (isinstance(person.prey_color,Tuple) and len(person.prey_color) == 3 and check_color_tuple(person.prey_color)))):
        print("Prey color falesafe triggered")
        prey_color = "blue"
    else:
        prey_color = person.prey_color
    if not(hasattr(person,"predator_color") and (isinstance(person.predator_color, str) or (isinstance(person.predator_color, Tuple) and len(person.predator_color) == 3 and check_color_tuple(person.predator_color)))):
        print("Predator color falesafe triggered")
        predator_color = "blue"
    else:
        predator_color = person.predator_color
    if not hasattr(person,"prey_placement_function") or not isinstance(person.prey_placement_function,Callable) or not test_function_time(2, person.prey_placement_function, World(), 1):
        print("Prey placement function failsafe 1 triggered")
        prey_placement_function = default_placement_function
    else:
        prey_placement_function = person.prey_placement_function
    if not hasattr(person,"predator_placement_function") or not isinstance(person.predator_placement_function,Callable) or not test_function_time(2, person.predator_placement_function, World(), 1):
        print("Predator placement function failsafe 1 triggered")
        predator_placement_function = default_placement_function
    else:
        predator_placement_function = person.predator_placement_function
    test_turtle = CompetitionTurtle(team_name, True, prey_color, World().random_location()[0], World().random_location()[1],
                                           Barrier(1), Barrier(1), Queue(), Lock(), can_goto, can_eat, 30)
    test_turtle.hide()
    if not hasattr(person,"prey_movement_function") or not isinstance(person.prey_movement_function,Callable) or not test_function_time(5, person.prey_movement_function, test_turtle, World()):
        print("Prey movement function failsafe 1 triggered")
        prey_movement_function = default_movement_function
    else:
        prey_movement_function = person.prey_movement_function
    test_turtle = CompetitionTurtle(team_name, False, predator_color, World().random_location()[0],
                                    World().random_location()[1],
                                    Barrier(1), Barrier(1), Queue(), Lock(), can_goto, can_eat, 30)
    test_turtle.hide()
    if not hasattr(person,"predator_movement_function") or not isinstance(person.predator_movement_function,Callable) or not test_function_time(5, person.predator_movement_function, test_turtle, World()):
        print("Predator movement function failsafe 1 triggered")
        predator_movement_function = default_movement_function
    else:
        predator_movement_function = person.predator_movement_function
    return Player(team_name,prey_color,predator_color,prey_placement_function,predator_placement_function,prey_movement_function,predator_movement_function)


people=[]
for file in os.listdir(turtle_programs.__path__[0]):
    if file.endswith(".py") and file != "__init__.py":
        person = import_module("turtle_programs."+ file.replace(".py","").strip())
        person = failsafes(person)
        people.append(person)



winner = run_match(people)

