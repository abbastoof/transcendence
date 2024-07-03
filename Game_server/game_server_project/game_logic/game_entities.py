import math
from game_defaults import *

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

# Paddle class
# Represents a paddle in the game world
# Properties:
#    - position: the position of the paddle
#    - width: the width of the paddle (read only)
#    - depth: the depth of the paddle (read only)
class Paddle:
    def __init__(self, x_position: float):
        self._position: Position = Position(x_position, 0, FIELD_WIDTH / 2)
        self._width: float = PADDLE_WIDTH
        self._depth: float = PADDLE_DEPTH
    
    # getter for position
    @property
    def position(self) -> Position:
        return self._position
    
    # getter for x
    @property
    def x(self) -> float:
        return self._position.x
    
    # getter for z
    @property
    def z(self):
        return self._position.z
    
    # getter for width
    @property
    def width(self) -> float:
        return self._width

    # getter for depth
    @property
    def depth(self) -> float:
        return self._depth

    # move method
    # moves the paddle by the given delta z
    def move(self, delta_z: float) -> None:
        ## TODO: make sure paddle doesn't move out of bounds
        self.position.move(0, 0, delta_z)

# Player class
# Represents a player in the game
# Properties:
#   - id: the id of the player
#   - paddle: the paddle of the player
#   - score: the score of the player
class Player:
    def __init__(self, id: int, x_position: float):
        self._id: int = id
        self._paddle: Paddle = Paddle(x_position)
        self._score: int = 0

    # getter for id
    @property
    def id(self) -> int:
        return self._id
    
    # getter for paddle
    @property
    def paddle(self) -> Paddle:
        return self._paddle

    # getter for score
    @property
    def score(self) -> int:
        return self._score
    
    # setter for score
    @score.setter
    def score(self, new_score: int) -> None:
        self._score = new_score

    # move_paddle method
    # moves the player's paddle by the given delta z
    def move_paddle(self, delta_z: float) -> None:
        self.paddle.move(delta_z)

    # update_score method
    # increments the player's score by 1
    def update_score(self) -> None:
        self._score += 1

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
# class Wall:
#     def __init__(self, x, z):


# GameState class
# Represents the state of the game
# Properties:
#  - game_id: the id of the game
#  - player1: the first player
#   - player2: the second player
#   - ball: the ball in the game
#   - time_remaining: the time remaining in the game
#   - current_rally: length of current rally so far
#   - longest_rally: length of the longest rally in the game
#   - total_hits: total number of hits in the game
#   - paused: whether the game is paused or not
class GameState:
    def __init__(self, game_id: int, player1: Player, player2: Player, ball: Ball):
        self._game_id: int = game_id
        self._player1: Player = player1
        self._player2: Player = player2
        self._ball: Ball = ball
        self._time_remaining: int = GAME_DURATION
        self._current_rally: int = 0
        self._longest_rally: int = 0
        self._total_hits: int = 0
        self._paused: bool = True
    
    # getter for game_id
    @property
    def game_id(self):
        return self._game_id

    # getter for player1
    @property
    def player1(self):
        return self._player1

    # getter for player2
    @property
    def player2(self):
        return self._player2
    
    # getter for ball
    @property
    def ball(self):
        return self._ball
    
    # getter for time_remaining
    @property
    def time_remaining(self):
        return self._time_remaining
    
    # setter for time_remaining
    @property
    def current_rally(self):
        return self._current_rally
    
    # setter for current_rally
    @current_rally.setter
    def current_rally(self, new_value):
        self._current_rally = new_value
    
    # getter for longest_rally
    @property
    def longest_rally(self):
        return self._longest_rally
    
    # setter for longest_rally
    @longest_rally.setter
    def longest_rally(self, new_value):
        self._longest_rally = new_value

    # get_player_score method
    # returns the score of the player with the given id
    # raises a ValueError if the player id is invalid
    def get_player_score(self, player_id):
        if player_id == self.player1.id:
            return self.player1.score
        elif player_id == self.player2.id:
            return self.player2.score
        else:
            raise ValueError("Invalid player ID")

    # update_player_score method
    # increments the score of the player with the given id
    # raises a ValueError if the player id is invalid
    def update_player_score(self, player_id):
        if player_id == self.player1.id:
            self.player1.update_score()
        elif player_id == self.player2.id:
            self.player2.update_score()
        else:
            raise ValueError("Invalid player ID")
    
    # getter for paused
    # returns whether the game is paused or not
    @property
    def paused(self):
        return self._paused
    
    # setter for paused
    # sets whether the game is paused or not
    @paused.setter
    def paused(self, new_value):
        self._paused = new_value

    # increase_ball_speed method
    # increases the speed of the ball by the given increment
    def increase_ball_speed(self, increment):
        self.ball.speed_up(increment)

    # handle_collisions method
    # handles the collisions between the ball and the walls or paddles
    # and updates the ball's direction accordingly
    def handle_collisions(self):
        if self.ball.z == 0 or self.ball.z == 300:
            self.ball.bounce_from_wall()
        # if self.ball.check_collision(self.player1.paddle):
        #     self.ball.bounce_from_paddle(self.player1.paddle)
        #     pass
        # if self.ball.check_collision(self.player2.paddle):
        #     self.ball.bounce_from_paddle(self.player2.paddle)
        #     pass

    # check_goal method
    # checks if the ball has scored a goal
    # and updates the score of the appropriate player
    # returns True if a goal was scored, False otherwise
    def check_goal(self):
        if self.ball.x < 0:
            self.update_player_score(self.player2.id)
            return True
        if self.ball.x > 400:
            self.update_player_score(self.player1.id)
            return True
        return False
        # check if someone scored goal

    #def reset_after_goal(self)
        # self.ball.reset()
        # self.ball.direction(here we get a random angle from a specified)

    # update_game_state method
    # updates the state of the game for the next frame
    # including updating the ball's position, handling collisions, and checking for goals
    # and increments the rally_timer
    def update_game_state(self):
        self.current_rally += 1
        self.ball.update_position()
        self.handle_collisions()
        if self.check_goal() == True:
            self.paused = True
    
    # run_rally method
    # runs a rally of the game
    # updates the game state until a goal is scored
    # then updates ball_position for 60 frames as ball goes through the goal
    # updates the longest rally if necessary
    # resets the current rally timer
    def run_rally(self): # reset ball position in this method? receive new angle as argument?
        self.paused = False
        while self.paused == False:
            self.update_game_state()
        for counter in range(60):
            self.ball.update_position()
        if self.current_rally > self.longest_rally:
            self.longest_rally = self.current_rally
        self.current_rally = 0
        
        # and movement handling?

    # def reset_game(self):
        # self.player1.score = 0
        # self.player1.score = 0
        # self.ball.reset()
        # self.ball.direction(default direction)

    # def handle_input(self, input)

    # def send_game_state_to_client(self):