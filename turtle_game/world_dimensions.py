class WorldDimensions:
    def __init__(self, width: float, height: float,):
        self.__min_x: float = -width / 2
        self.__min_y: float = -height / 2
        self.__max_x: float = width / 2
        self.__max_y: float = height / 2
        self.__width: float = width
        self.__height: float = height

    def min_x(self):
        return self.__min_x

    def min_y(self):
        return self.__min_y

    def max_x(self):
        return self.__max_x

    def max_y(self):
        return self.__max_y

    def width(self):
        return self.__width

    def height(self):
        return self.__height
