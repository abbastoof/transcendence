import math
from game_defaults import *

class Paddle:
    def __init__(self, x_position):
        self._position = {'x': x_position, 'y': 0, 'z': FIELD_WIDTH / 2}
        self._width = PADDLE_WIDTH
        self._depth = PADDLE_DEPTH
    
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, new_position):
        ## TODO: make sure position can't be set out of playing field
        if 'x' in new_position:
            self._position['x'] = new_position['x']
        if 'z' in new_position:
            self._position['z'] = new_position['z']

    @property
    def x(self):
        return self._position['x']

    @x.setter
    def x(self, value):
        ## TODO: make sure position can't be set out of playing field
        self.position['x'] = value

    @property
    def z(self):
        return self._position['z']

    @z.setter
    def z(self, value):
        ## TODO: make sure position can't be set out of playing field
        self._position['z'] = value
    
    @property
    def width(self):
        return self._width

    @property
    def depth(self):
        return self._depth

    def move(self, delta_z):
        ## TODO: make sure paddle doesn't move out of bounds
        self._position['z'] += delta_z

class Player:
    def __init__(self, id, x_position):
        self._id = id
        self._paddle = Paddle(x_position)
        self._score = 0

    @property
    def id(self):
        return self._id
    
    @property
    def paddle(self):
        return self._paddle

    @property
    def score(self):
        return self._score
    
    @score.setter
    def score(self, new_score):
        self._score = new_score

    def move_paddle(self, delta_z):
        self.paddle.move(delta_z)

    def update_score(self):
        self._score += 1

class Ball:
    def __init__(self, x_position, z_position, radius, speed, direction):
        self._position = {'x': x_position, 'y': 0, 'z': z_position}
        self._radius = radius
        self._speed = speed
        self._direction = direction ## degrees or rads? i'd say degrees
    
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, new_position):
        ## TODO: make sure position can't be set out of playing field
        if 'x' in new_position:
            self._position['x'] = new_position['x']
        if 'z' in new_position:
            self._position['z'] = new_position['z']

    @property
    def x(self):
        return self._position['x']

    @x.setter
    def x(self, value):
        ## TODO: make sure position can't be set out of playing field
        self.position['x'] = value

    @property
    def z(self):
        return self._position['z']

    @z.setter
    def z(self, value):
        ## TODO: make sure position can't be set out of playing field
        self._position['z'] = value

    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, new_radius):
        ## TODO: maybe protect this some way?
        self._radius = new_radius

    @property
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self, new_speed):
        self._speed = new_speed

    @property
    def direction(self):
        return self._direction
    
    @direction.setter
    def direction(self, new_direction):
        self._direction = new_direction

    def speed_up(self, increment):
        self._speed += increment

    def update_position(self):
        radians = math.radians(self._direction)
        self._position['x'] += math.cos(radians) * self._speed
        self._position['z'] += math.sin(radians) * self._speed
    
    def check_collision(self, object):
        # collision checking algorithm, can be wall or paddle
        return True # (or False)
 
    # def bounce_from_paddle(self, paddle):
        # determine new direction for the ball when it hits the paddle. see game design doc
        # taking paddle as argument to calculate the new angle based on where the ball hits the paddle
    
    def bounce_from_wall(self):
        self._direction = (360 - self._direction) % 360
        # reflects the direction when ball bounces from wall

    # def reset_ball(self):
        # this would reset ball position to the centre 
# class Wall:
#     def __init__(self, x, z):



class GameState:
    def __init__(self, game_id, player1, player2, ball):
        self.game_id = game_id
        self.player1 = player1
        self.player2 = player2
        self.ball = ball
        self.time_remaining = GAME_DURATION
        self.current_rally = 0
        self.longest_rally = 0
    
    @property
    def game_id(self):
        return self._game_id

    @property
    def player1(self):
        return self._player1

    @property
    def player2(self):
        return self._player2
    
    @property
    def ball(self):
        return self._ball
    
    @property
    def time_remaining(self):
        return self._time_remaining
    
    @property
    def current_rally(self):
        return self._current_rally
    
    @property
    def longest_rally(self):
        return self._longest_rally
    
    @longest_rally.setter
    def longest_rally(self, new_value):
        self._longest_rally = new_value

    def get_player_score(self, player_id):
        if player_id == self.player1.id:
            return self.player1.score
        elif player_id == self.player2.id:
            return self.player2.score
        else:
            raise ValueError("Invalid player ID")

    def update_player_score(self, player_id):
        if player_id == self.player1.id:
            self.player1.score += 1
        elif player_id == self.player2.id:
            self.player2.score += 1
        else:
            raise ValueError("Invalid player ID")

    def increase_ball_speed(self, increment):
        self.ball.speed_up(increment)

    def handle_collisions(self):
        if self.ball.check_collision(self.player1.paddle):
            self.ball.bounce_from_paddle(self.player1.paddle)
            pass
        if self.ball.check_collision(self.player2.paddle):
            self.ball.bounce_from_paddle(self.player2.paddle)
            pass

    # def check_goal(self):
        # check if someone scored goal

    #def reset_after_goal(self)
        # self.ball.reset()
        # self.ball.direction(here we get a random angle from a specified)

    def update_game_state(self):
        self.handle_collisions()
        self.ball.update_position()
        # and more logic
        # and movement handling?

    # def reset_game(self):
        # self.player1.score = 0
        # self.player1.score = 0
        # self.ball.reset()
        # self.ball.direction(default direction)

    # def handle_input(self, input)

    # def send_game_state_to_client(self):