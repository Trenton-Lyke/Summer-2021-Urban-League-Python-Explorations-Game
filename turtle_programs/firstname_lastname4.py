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
    if turtle.is_turtle_on_left_edge():
        turtle.setheading(0)
        turtle.forward(turtle.max_speed())
    elif turtle.is_turtle_on_top_edge():
        turtle.setheading(270)
        turtle.forward(turtle.max_speed())
    elif turtle.is_turtle_on_right_edge():
        turtle.setheading(180)
        turtle.forward(turtle.max_speed())
    elif turtle.is_turtle_on_bottom_edge():
        turtle.setheading(90)
        turtle.forward(turtle.max_speed())
    else:
        if turtle.closest_enemy_predator().distance()>world.predator_kill_radius()*3:
            turtle.wait()
        else:
            angle = turtle.enemy_predators_relative_locations[0].angle()
            num = randint(0, 2)
            change = 180
            if num == 0:
                change = 90
            elif num == 1:
                change = -90
            turtle.setheading(angle + change)
            turtle.forward(turtle.energy_level() // 2)

def predator_movement_function(turtle: CompetitionTurtle, world):
    turtle.turn_to_closest_enemy_prey()
    turtle.forward(turtle.energy_level() / 2)


