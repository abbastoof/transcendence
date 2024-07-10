import math
from entities.position import Position
from game_defaults import *
from entities.paddle import Paddle
import logging
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
        self._delta_x: float = 0
        self._delta_z: float = 0
        self._radius: float = radius
        self._speed: float = speed
        self._direction: float = direction ## degrees or rads? i'd say degrees
        self.set_deltas()


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
        self.set_deltas()

    # getter for direction
    @property
    def direction(self) -> float:
        return self._direction
    
    # setter for direction
    @direction.setter
    def direction(self, value: float) -> None:
        self._direction = value
        self.set_deltas()

    def set_deltas(self) -> None:
        radians: float = math.radians(self.direction)
        self._delta_x = math.cos(radians) * self.speed
        self._delta_z = math.sin(radians) * self.speed
    
    @property
    def delta_x(self) -> float:
        return self._delta_x
    
    @property
    def delta_z(self) -> float:
        return self._delta_z
    
    # speed_up method
    # increases the speed of the ball by the given increment
    def speed_up(self, increment: float) -> None:
        self.speed += increment

    # update_position method
    # updates the position of the ball based on its speed and direction
    def update_position(self) -> None:
        self._position.x += self.delta_x
        self._position.z += self.delta_z
    
    # check_collision method
    # checks if the ball has collided with a given object
    def check_collision(self, paddle):
        # collision checking algorithm, can be wall or paddle
        if(self._position.x > 0 + PADDLE_DEPTH and self._position.x < FIELD_DEPTH - PADDLE_DEPTH):
            return False # (or False)
        paddle_z_bottom = paddle.z - PADDLE_WIDTH / 2 
        paddle_z_top = paddle_z_bottom + PADDLE_WIDTH
        if (self._position.z >= paddle_z_bottom and self._position.z <= paddle_z_top):
            return True
        return False
 
    def bounce_from_paddle(self, paddle):
        logging.info(f"Bouncing from paddle, paddle pos: x {paddle.position.x}, z {paddle.position.z} ")
        logging.info(f"Ball pos x: {self.x}, z: {self.z}")
        logging.info(f"Ball deltas before bounce: x {self.delta_x}, z {self.delta_z}")
        
        self.direction = self.direction % 360
        logging.info(f"Ball direction before bounce: {self.direction}")
        
    # Calculate hit position normalization
        hitpos = (self.z - paddle.position.z) / (paddle.width / 2)

        adjustment = self.direction % 45 + 5 * abs(hitpos)
        logging.info(f"hitpos variable: {hitpos}")
        logging.info(f"adjustment: {adjustment}")
        if hitpos >= 0 and hitpos < 0.2 or hitpos < 0 and hitpos > -.2:
            self.direction = 1 + (hitpos * 10) if self.delta_x < 0.0 else 183 + 5 * hitpos
        else:
            if self.delta_z < 0.0:
                if self.direction > 270:
                    if hitpos > 0.0:
                        self.direction = 170 - adjustment
                    else:
                        self.direction = 190 + adjustment
                else:
                    if hitpos > 0.0:
                        self.direction = 10 + adjustment
                    else:
                        self.direction = 350 - adjustment
            else:
                if self.direction > 90:
                    if hitpos > 0.0:
                        self.direction = 10 + adjustment
                    else:
                        self.direction = 350 - adjustment
                else:
                    if hitpos > 0.0:
                        self.direction = 170 - adjustment
                    else:
                        self.direction = 190 + adjustment
                

        logging.info(f"Direction after bounce: {self.direction}")
        logging.info(f"Deltas after bounce: x {self.delta_x}, y {self.delta_z}")
        #conditions
        # direction -90 - 0 / 270 - 360 aka bottomright
        # if hitpos < 0
        # desired angle between 180 & 270 aka bottom left
        # if hitpos > 0
        # desired angle between 90 & 180 aka top left
        
        # direction 180 - 270 aka bottom left
        # if hitpos < 0
        # desired angle between 270 & 360 aka bottom right
        # if hitpos > 0
        # desired angle between 0 & 90 aka top right
        
        # direction 0 - 90 aka top right
        # if hitpos > 0
        # desired angle between 90 & 180 aka top left
        # if hitpos < 0 
        # desired angle between 180 & 270 aka bottom left

        # direction 90 - 180 aka top left
        # if hitpos > 0
        # desired angle between 0 & 90 aka top right
        # if hitpos < 0
        # desired angle between 180 & 270 aka


        #taking paddle as argument to calculate the new angle based on where the ball hits the paddle
    
    # bounce_from_wall method
    # reflects the direction of the ball when it bounces from a wall
    def bounce_from_wall(self) -> None:
        self.direction = (360 - self.direction) % 360
        # reflects the direction when ball bounces from wall

    # def reset_ball(self):
        # this would reset ball position to the centre 
