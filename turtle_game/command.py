from typing import Callable


class Command:
    def __init__(self, function: Callable[[float],None], value: float):
        self.function: Callable[[float],None] = function
        self.value: float = value