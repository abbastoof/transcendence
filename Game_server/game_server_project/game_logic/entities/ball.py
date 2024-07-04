import math
from entities.position import Position

# Ball class
# Represents a ball in the game
# Properties:
#   - position: the position of the ball
#   - radius: the radius of the ball
#   - speed: the speed of the ball
#   - direction: the direction of the ball
class Ball:
    def __init__(self, x: float, z: float, radius: float, speed: float, direction: float):
        self._position: Position = Position(x, 0, z)
        self._radius: float = radius
        self._speed: float = speed
        self._direction: float = direction ## degrees or rads? i'd say degrees

    # getter for position    
    @property
    def position(self) -> float:
        return self._position
    
    # setter for position
    @position.setter
    def position(self, new_position):
        new_x, new_y, new_z = new_position
        self._position.x = new_x
        self._position.y = new_y
        self._position.z = new_z

    # getter for x
    @property
    def x(self) -> float:
        return self._position.x

    # setter for x
    @x.setter
    def x(self, value: float) -> None:
        ## TODO: make sure position can't be set out of playing field
        self._position.x = value

    # getter for z
    @property
    def z(self) -> float:
        return self._position.z

    # setter for z
    @z.setter
    def z(self, value: float) -> None:
        ## TODO: make sure position can't be set out of playing field
        self._position.z = value

    # getter for radius
    @property
    def radius(self) -> float:
        return self._radius
    
    # setter for radius
    @radius.setter
    def radius(self, value: float) -> None:
        ## TODO: maybe protect this some way?
        self._radius = value

    # getter for speed
    @property
    def speed(self) -> float:
        return self._speed
    
    # setter for speed
    @speed.setter
    def speed(self, value: float) -> None:
        self._speed = value

    # getter for direction
    @property
    def direction(self) -> float:
        return self._direction
    
    # setter for direction
    @direction.setter
    def direction(self, value: float) -> None:
        self._direction = value

    # speed_up method
    # increases the speed of the ball by the given increment
    def speed_up(self, increment: float) -> None:
        self._speed += increment

    # update_position method
    # updates the position of the ball based on its speed and direction
    def update_position(self) -> None:
        radians: float = math.radians(self._direction)
        self._position.x += math.cos(radians) * self._speed
        self._position.z += math.sin(radians) * self._speed
    
    # check_collision method
    # checks if the ball has collided with a given object
    def check_collision(self, object):
        # collision checking algorithm, can be wall or paddle
        return True # (or False)
 
    # def bounce_from_paddle(self, paddle):
        # determine new direction for the ball when it hits the paddle. see game design doc
        # taking paddle as argument to calculate the new angle based on where the ball hits the paddle
    
    # bounce_from_wall method
    # reflects the direction of the ball when it bounces from a wall
    def bounce_from_wall(self) -> None:
        self._direction = (360 - self._direction) % 360
        # reflects the direction when ball bounces from wall

    # def reset_ball(self):
        # this would reset ball position to the centre 