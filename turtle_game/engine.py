from math import sqrt, degrees, atan2
from queue import Queue
from random import random
from threading import Barrier, Lock, Thread, Event
from typing import Tuple, List, Callable, Dict
from turtle import tracer, update



from turtle_game.competition_turtle import CompetitionTurtle
from turtle_game.relative_location import RelativeLocation
from turtle_game.game_data_entry import GameDataEntry

from turtle_game.player import Player
from turtle_game.stoppable_thread import StoppableThread
from turtle_game.world import World





class Engine:
    def __init__(self, world: World, players: List[Player], prey_per_team:int=125, predators_per_team:int=25, border_proximity:float=10, safe_mode: bool=False):
        self.safe_mode = safe_mode
        self.world: World = world
        self.predator_kill_radius: int = world.predator_kill_radius()
        self.players: List[Player] = players
        parties = len(players) * (prey_per_team + predators_per_team) + 1
        self.move_barrier: Barrier = Barrier(parties)
        self.check_barrier: Barrier = Barrier(parties)
        self.process_queue: Queue = Queue()
        self.game_lock: Lock = Lock()
        self.write_lock: Lock = Lock()
        self.movement_functions_dict: Dict[str, Dict[bool, Callable[[CompetitionTurtle], None]]] = {}
        self.__border_proximity = border_proximity
        self.__start: bool = False


        for player in players:
            tracer(0, 0)
            self.movement_functions_dict[player.team_name] = {True: player.prey_movement_function, False: player.predator_movement_function}
            for i in range(prey_per_team):
                location = player.prey_placement_function(self.world, i)
                location = self.location_failsafe(location, True)
                turtle = CompetitionTurtle(player.team_name, True, player.prey_color, location[0], location[1],
                                           self.move_barrier, self.check_barrier, self.process_queue, self.game_lock, self.can_move_without_wait, self.can_eat, self.game_over, self.is_turtle_on_left_edge, self.is_turtle_on_top_edge, self.is_turtle_on_right_edge, self.is_turtle_on_bottom_edge, self.is_turtle_in_top_left_corner, self.is_turtle_in_top_right_corner, self.is_turtle_in_bottom_right_corner, self.is_turtle_in_bottom_left_corner, 9)
                self.world.turtles.append(turtle)
                self.world.prey.append(turtle)

            for i in range(predators_per_team):
                location = player.predator_placement_function(self.world, i)
                location = self.location_failsafe(location, False)
                turtle = CompetitionTurtle(player.team_name, False, player.predator_color, location[0], location[1],
                                           self.move_barrier, self.check_barrier, self.process_queue, self.game_lock, self.can_move_without_wait, self.can_eat, self.game_over, self.is_turtle_on_left_edge, self.is_turtle_on_top_edge, self.is_turtle_on_right_edge, self.is_turtle_on_bottom_edge, self.is_turtle_in_top_left_corner, self.is_turtle_in_top_right_corner, self.is_turtle_in_bottom_right_corner, self.is_turtle_in_bottom_left_corner, 12)
                self.world.turtles.append(turtle)
                self.world.predators.append(turtle)

        tracer(0, 0)
        while(not self.check_turtles(False)):
            pass
        update()

    def location_failsafe(self, location, is_prey):
        if not (isinstance(location, Tuple) and len(location) == 2 and isinstance(location[0], float) and isinstance(
                location[1], float)):
            print(("Prey" if is_prey else "Predator"),"placement function failsafe 2 triggered")
            location = self.world.random_location()
        return location


    def can_move_without_wait(self, turtle: CompetitionTurtle):
        return not self.__start or not self.world.is_in_bounds(turtle)
    def can_eat(self, predator: CompetitionTurtle, prey: CompetitionTurtle):
        return not predator.is_prey() and prey.is_prey() and predator.distance(prey) < self.predator_kill_radius




    def check_turtles(self, can_die: bool)->bool:
        for turtle in self.world.turtles:
            if not self.move_inbounds(turtle) and not can_die:
                return False
            if not self.update_engine_lists(can_die, turtle) and not can_die:
                return False
            turtle.ally_predators_relative_locations.sort(key=lambda x: x.distance())
            turtle.ally_prey_relative_locations.sort(key=lambda x: x.distance())
            turtle.enemy_predators_relative_locations.sort(key=lambda x: x.distance())
            turtle.enemy_prey_relative_locations.sort(key=lambda x: x.distance())
        return True



    def update_engine_lists(self, can_die: bool, turtle: CompetitionTurtle)-> bool:
        turtle.ally_predators_relative_locations = []
        turtle.ally_prey_relative_locations = []
        turtle.enemy_predators_relative_locations = []
        turtle.enemy_prey_relative_locations = []
        for other_turtle in self.world.turtles:
            if turtle != other_turtle:
                distance = turtle.distance(other_turtle)
                angle = turtle.angle(other_turtle)
                if turtle.team_name() == other_turtle.team_name():
                    if other_turtle.is_prey():
                        turtle.ally_prey_relative_locations.append(RelativeLocation(angle, distance))
                    else:
                        turtle.ally_predators_relative_locations.append(RelativeLocation(angle, distance))
                else:
                    if other_turtle.is_prey():
                        if self.can_eat(turtle, other_turtle):
                            if can_die:
                                turtle.eat(other_turtle)
                                other_turtle.hide()
                                self.world.prey[:] = [x for x in self.world.prey if not x == other_turtle]
                                self.world.turtles[:] = [x for x in self.world.turtles if not x == other_turtle]
                            else:
                                location = self.world.random_location()
                                other_turtle.goto(location[0],location[1])
                                return False
                        turtle.enemy_prey_relative_locations.append(RelativeLocation(angle, distance))
                    else:
                        turtle.enemy_predators_relative_locations.append(RelativeLocation(angle, distance))
        return True


    def move_inbounds(self, turtle):
        x = turtle.position()[0]
        y = turtle.position()[1]
        stayed = True
        if x > self.world.world_dimensions.max_x():
            turtle.force_heading(360-(turtle.heading()+180))
            turtle.goto(self.world.world_dimensions.max_x(), y)
            stayed = False
        elif x < self.world.world_dimensions.min_x():
            turtle.force_heading(360-(turtle.heading()+180))
            turtle.goto(self.world.world_dimensions.min_x(), y)
            stayed = False
        if y > self.world.world_dimensions.max_y():
            turtle.force_heading(360 - turtle.heading())
            turtle.goto(x, self.world.world_dimensions.max_y())
            stayed = False
        elif y < self.world.world_dimensions.min_y():
            turtle.force_heading(360 - turtle.heading())
            turtle.goto(x, self.world.world_dimensions.min_y())
            stayed = False
        return stayed

    def number_prey_alive(self, player: Player) -> int:
        return len(list(filter(lambda x: x.team_name() == player.team_name, self.world.prey)))

    def game_over(self) -> bool:
        count = 0
        for player in self.players:
            count += 1 if (self.number_prey_alive(player) > 0) else 0
        return count <= 1

    def is_turtle_on_left_edge(self, turtle: CompetitionTurtle) -> bool:
        return abs(turtle.position()[0]-self.world.world_dimensions.min_x()) < self.__border_proximity
    def is_turtle_on_top_edge(self, turtle: CompetitionTurtle) -> bool:
        return abs(turtle.position()[1] - self.world.world_dimensions.max_y()) < self.__border_proximity
    def is_turtle_on_right_edge(self, turtle: CompetitionTurtle) -> bool:
        return abs(turtle.position()[0] - self.world.world_dimensions.max_x()) < self.__border_proximity
    def is_turtle_on_bottom_edge(self, turtle: CompetitionTurtle) -> bool:
        return abs(turtle.position()[1] - self.world.world_dimensions.min_y()) < self.__border_proximity
    def is_turtle_in_top_left_corner(self, turtle: CompetitionTurtle) -> bool:
        return self.is_turtle_on_left_edge(turtle) and self.is_turtle_on_top_edge(turtle)
    def is_turtle_in_top_right_corner(self, turtle: CompetitionTurtle) -> bool:
        return self.is_turtle_on_right_edge(turtle) and self.is_turtle_on_top_edge(turtle)
    def is_turtle_in_bottom_right_corner(self, turtle: CompetitionTurtle) -> bool:
        return self.is_turtle_on_right_edge(turtle) and self.is_turtle_on_bottom_edge(turtle)
    def is_turtle_in_bottom_left_corner(self, turtle: CompetitionTurtle) -> bool:
        return self.is_turtle_on_left_edge(turtle) and self.is_turtle_on_bottom_edge(turtle)
    def winning_player(self) -> Player:
        for player in self.players:
            if (self.number_prey_alive(player) > 0):
                return player

    def turtle_thread_function(self, function: Callable[[CompetitionTurtle, World], None], turtle: CompetitionTurtle):

        invalid_function: bool = False
        while not self.game_over():
            if not invalid_function:
                turtle.reset_wait()
                try:
                    if self.safe_mode:
                        test_thred = StoppableThread(target=function,args=(turtle, self.world,))
                        test_thred.start()

                        while test_thred.is_alive():
                            Event().wait(timeout=.25)
                            if not turtle.did_wait():
                                turtle.wait()
                                test_thred.stop()
                                invalid_function = True
                    else:
                        function(turtle, self.world)
                except Exception as e:
                    print(e)
                    turtle.wait()
                if not turtle.did_wait():
                    print(("Prey" if turtle.is_prey() else "Predator"),"movement function failsafe 2 triggered (turtle did not wait)")
                    turtle.wait()
            else:
                print(("Prey" if turtle.is_prey() else "Predator"), "movement function failsafe 3 triggered (turtle took too long to decide turn) shutting down turtle behavior")
                turtle.wait()

    def start_threads(self):
        for turtle in self.world.turtles:
            turtle.start()
            thread = Thread(target=(self.turtle_thread_function), args=(self.movement_functions_dict[turtle.team_name()][turtle.is_prey()], turtle))
            thread.setDaemon(True)
            thread.start()

    def run(self):
        self.__start = True
        self.start_threads()
        old_count = len(self.world.turtles)
        while not self.game_over():
            try:
                self.move_barrier.wait()
            except:
                pass
            tracer(0, 0)
            while not self.process_queue.empty():
                command = self.process_queue.get()
                command.function(command.value)

            self.check_turtles(True)
            update()
            if(old_count != len(self.world.turtles)):
                for player in self.players:
                    print(GameDataEntry(player.team_name, self.number_prey_alive(player)))
                old_count = len(self.world.turtles)
            try:
                self.check_barrier.wait()
            except:
                pass
        print("Winner:",self.winning_player().team_name)
        return self.winning_player()



