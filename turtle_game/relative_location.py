class RelativeLocation:
    def __init__(self, angle: float, distance: float):
        self.__angle: float = angle
        self.__distance: float = distance

    def angle(self) -> float:
        return self.__angle

    def distance(self) -> float:
        return self.__distance

    def __str__(self):
        return ("angle: "+str(self.angle)+" distance: "+str(self.distance))

