#billy_batson
from random import randint

from turtle_game.competition_turtle import CompetitionTurtle

team_namer="team name"

prey_color = "purple"

predator_color = "green"

def prey_placement_function(world, prey_number):
    return world.random_location()

def predator_placement_function(world, prey_number):
    return world.random_location()

def prey_movement_function(turtle: CompetitionTurtle, world):
    for i in range(1000):
        turtle.forward(turtle.energy_level() / 2)

def predator_movement_function(turtle: CompetitionTurtle, world):
        turtle.forward(turtle.energy_level() / 2)


