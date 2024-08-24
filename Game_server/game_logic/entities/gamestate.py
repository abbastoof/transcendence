from game_logic.entities.player import Player
from game_logic.entities.ball import Ball
from game_logic.game_defaults import *
import random
import time
import asyncio
import logging

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
        self._paused: bool = True
        self._in_progress: bool = True
        self._bounce: bool = False
        self._hitpos: float = 0.0
    
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

    @property
    def bounce(self):
        return self._bounce
    
    @bounce.setter
    def bounce(self, new_value):
        self._bounce = new_value

    @property
    def hitpos(self):
        return self._hitpos

    @hitpos.setter
    def hitpos(self, new_value):
        self._hitpos = new_value
        
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
    def paused(self) -> bool:
        return self._paused
    
    # setter for paused
    # sets whether the game is paused or not
    @paused.setter
    def paused(self, new_value) -> None:
        self._paused = new_value
    
    # getter for in_progress
    @property
    def in_progress(self) -> bool:
        return self._in_progress
    
    @in_progress.setter
    def in_progress(self, new_value) -> None:
        self._in_progress = new_value

    # move_player method
    # moves the paddle of the player with the given id by the given delta z 
    # raises a ValueError if the player id is invalid
    def move_player(self, player_id: int, delta_z: float) -> None:
        if player_id == self.player1.id:
            self.player1.move_paddle(delta_z)
        elif player_id == self.player2.id:
            self.player2.move_paddle(delta_z)
        else:
            logging.error("Invalid player ID")

    # increase_ball_speed method
    # increases the speed of the ball by the given increment
    def increase_ball_speed(self, increment: float) -> None:
        self.ball.speed_up(increment)

    # handle_collisions method
    # handles the collisions between the ball and the walls or paddles
    # and updates the ball's direction and player's hitcount accordingly
    def handle_collisions(self) -> None:
        self.bounce = False
        if self.ball.x < 0 or self.ball.x > FIELD_DEPTH:
            return
        if self.ball.z - BALL_RADIUS <= 0 or self.ball.z + BALL_RADIUS >= FIELD_WIDTH:
            self.ball.bounce_from_wall()
        elif self.ball.check_collision(self.player1.paddle):
            self.player1.add_hit()
            self.bounce = True
            self.hitpos = self.ball.bounce_from_paddle(self.player1.paddle)
        elif self.ball.check_collision(self.player2.paddle):
            self.player2.add_hit()
            self.bounce = True
            self.hitpos = self.ball.bounce_from_paddle(self.player2.paddle)
            
    # check_goal method
    # checks if the ball has scored a goal
    # and updates the score of the appropriate player
    # returns True if a goal was scored, False otherwise
    def check_goal(self) -> None:
        if self.ball.x < 0:
            self.update_player_score(self.player2.id)
            return True
        elif self.ball.x > FIELD_DEPTH:
            self.update_player_score(self.player1.id)
            return True
        return False

    # reset_ball method
    # resets the ball to the center of the field
    # and gives it a random direction
    def reset_ball(self):
        if self.ball.x < 0:
            self.ball.direction = random.randrange(-40, 40) #random direction towards player 2 
        elif self.ball.x > FIELD_DEPTH:
            self.ball.direction = random.randrange(140, 220)  #random direction towards player 1
        else:
            if random.random() >= .5:
                self.ball.direction = random.randrange(-12, 12)
            else:
                self.ball.direction = random.randrange(168, 192)
        self.ball.speed = BALL_SPEED
        self.ball.position = BALL_DEFAULT_X, 0, BALL_DEFAULT_Z

    # is_game_over method
    # returns True if the game is over, False otherwise
    def is_game_over(self) -> bool:
        return self.time_remaining <= 0 or self.player1.score >= 10 or self.player2.score >= 10
