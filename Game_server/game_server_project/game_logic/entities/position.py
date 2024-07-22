# Position class
# Represents a 3d position in the game world
# Properties:
#    - x: the x coordinate of the position
#    - y: the y coordinate of the position
#    - z: the z coordinate of the position
class Position:
    def __init__(self, x: float, y: float, z: float):
        self._x: float = x
        self._y: float = y
        self._z: float = z
    
    # getter for x
    @property
    def x(self) -> float:
        return self._x
    
    # setter for x
    @x.setter
    def x(self, value: float) -> None:
        self._x = value

    # getter for y
    @property
    def y(self) -> float:
        return self._y
    
    # setter for y
    @y.setter
    def y(self, value: float) -> None:
        self._y = value

    # getter for z
    @property
    def z(self) -> float:
        return self._z
    
    # setter for z
    @z.setter
    def z(self, value: float) -> None:
        self._z = value

    def as_tuple(self) -> tuple:
        return self._x, self._y, self._z
    
    # move method
    # moves the position by the given deltas
    def move(self, delta_x: float, delta_y: float, delta_z: float):
        self._x += delta_x
        self._y += delta_y
        self._z += delta_z

    # __eq__ method
    # compares two positions for equality
    def __eq__(self, other) -> bool:
        if isinstance(other, Position):
            return self._x == other.x and self._y == other.y and self._z == other.z
        return False