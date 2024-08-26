import math
from game_logic.entities.position import Position
from game_logic.game_defaults import *
from game_logic.entities.paddle import Paddle
from game_logic.game_defaults import *
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

    # getter for y
    @property
    def y(self) -> float:
        return self._position.y

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

    # set_deltas method
    # calculates the x and z deltas based on the speed and direction of the ball
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
    # collision check algorithm with paddle
    # returns false if no collision, true if collision
    # takes a paddle as argument
    # returns false immediately if ball is not in same x coordinates as paddles
    def check_collision(self, paddle):
        # Calculate the ball's next position
        expected_x = self.position.x + self.delta_x
        expected_z = self.position.z + self.delta_z

        # Check collision for the left paddle (positioned at x = 0)
        if paddle.x == PLAYER1_START_X and expected_x - BALL_RADIUS <= 0:
            # Calculate the paddle's boundaries along the z-axis
            paddle_z_bottom = paddle.z - PADDLE_WIDTH / 2
            paddle_z_top = paddle.z + PADDLE_WIDTH / 2

            # Check if the ball's z position is within the paddle's z-axis range
            if paddle_z_bottom <= expected_z <= paddle_z_top:
                return True  # Collision detected

        # Check collision for the right paddle (positioned at x = FIELD_DEPTH)
        elif paddle.x == PLAYER2_START_X and expected_x + BALL_RADIUS >= FIELD_DEPTH:
            # Calculate the paddle's boundaries along the z-axis
            paddle_z_bottom = paddle.z - PADDLE_WIDTH / 2
            paddle_z_top = paddle.z + PADDLE_WIDTH / 2

            # Check if the ball's z position is within the paddle's z-axis range
            if paddle_z_bottom <= expected_z <= paddle_z_top:
                return True  # Collision detected

        return False  # No collision

    
    # bounce_from_paddle method
    # reflects the direction of the ball when it bounces from a paddle
    # takes a paddle as argument
    # updates the direction of the ball based on where it hits the paddle
    # and the direction it was going before collision
    def bounce_from_paddle(self, paddle) -> float:
        self.direction = self.direction % 360 # make sure direction is between 0 and 360
        hitpos = (self.z - paddle.position.z) / (paddle.width / 2) # hitpos: where the ball hits the paddle
        speedboost = abs(hitpos) * 1.2
        dz_factor = (self.delta_z / self.speed) * 10 # dz_factor: how much the ball is going up or down
        direction_mod = abs((self.direction % 180) - 90) 
        if direction_mod > MAX_BOUNCE_ANGLE_ADJUSTMENT:
            direction_mod = (MAX_BOUNCE_ANGLE_ADJUSTMENT * 2) - direction_mod # make sure direction_mod does not go above 80
        # direction_mod: absolute difference from a right angle (90 degrees)
        # treating angles within 15 degrees of 90 and 270 as tight angles.
        
        # adjustment: how much the direction of the ball should be adjusted
        adjustment = abs(MAX_BOUNCE_ANGLE_ADJUSTMENT - direction_mod) + 5 * abs(hitpos) + dz_factor
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)

        # if ball hits the middle of the paddle, it bounces with wider angle
        if hitpos >= 0 and hitpos < 0.2 or hitpos < 0 and hitpos > -.2:
            if (abs(hitpos) < 0.1):
                self.speed_up(1.3)
            else:
                self.speed_up(speedboost)
            logging.info(hitpos)
            if self.delta_z < 0.0:
                self.direction = 357 - (hitpos * adjustment) if self.delta_x < 0.0 else 177 - (hitpos * adjustment)
            else:
                self.direction = 3 + (hitpos * adjustment) if self.delta_x < 0.0 else 183 + (hitpos * adjustment)
        else:
            speedboost = abs(hitpos) * 1.2
            self.speed_up(speedboost)
            if self.delta_z < 0.0: # if ball is going down
                if self.direction > 270: # if ball is going right
                    if hitpos > 0.0: # if ball hits the top area of the paddle
                        self.direction = 170 - adjustment * 0.5 # bounce to top left
                    else: # if ball hits the bottom area of the paddle
                        self.direction = 190 + adjustment # bounce to bottom left
                else: # if ball is going left
                    if hitpos > 0.0: # if ball hits the top of the paddle
                        self.direction = 10 + adjustment * 0.5  # bounce to top right
                    else:
                        self.direction = 350 - adjustment # bounce to bottom right
            else: # if ball is going up
                if self.direction > 90: # if ball is going left
                    if hitpos > 0.0: # if ball hits the top area of the paddle
                        self.direction = 10 + adjustment # bounce to top right
                    else:
                        self.direction = 350 - adjustment * 0.5 # bounce to bottom right
                else: # if ball is going right
                    if hitpos > 0.0: # if ball hits the top area of the paddle
                        self.direction = 170 - adjustment # bounce to top left
                    else: # if ball hits the bottom area of the paddle
                        self.direction = 190 + adjustment * 0.5 # bounce to bottom left
        self.direction = self.direction % 360 # make sure direction is between 0 and 360

        return (abs(hitpos))

    # bounce_from_wall method
    # reflects the direction of the ball when it bounces from a wall
    def bounce_from_wall(self) -> None:
        self.direction = (360 - self.direction) % 360
        # reflects the direction when ball bounces from wall

