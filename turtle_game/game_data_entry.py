from typing import Union, Tuple


class GameDataEntry:
    def __init__(self, team_name: str, number_of_living_prey: int, color: Union[str,Tuple[float,float,float]]=""):
        self.team_name: str = team_name
        self.number_of_living_prey: int = number_of_living_prey
        self.color = color

    def __str__(self):
        return self.team_name+" "+str(self.number_of_living_prey)+" "+str(self.color)