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
    def paused(self) -> bool:
        return self._paused
    
    # setter for paused
    # sets whether the game is paused or not
    @paused.setter
    def paused(self, new_value) -> None:
        self._paused = new_value
    
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
        if self.ball.x < 0 or self.ball.x > FIELD_DEPTH:
            return
        if self.ball.z - BALL_RADIUS <= 0 or self.ball.z + BALL_RADIUS >= FIELD_WIDTH:
            self.ball.bounce_from_wall()
        elif self.ball.check_collision(self.player1.paddle):
            self.player1.add_hit()
            self.ball.bounce_from_paddle(self.player1.paddle)
        elif self.ball.check_collision(self.player2.paddle):
            self.player2.add_hit()
            self.ball.bounce_from_paddle(self.player2.paddle)
            
    # check_goal method
    # checks if the ball has scored a goal
    # and updates the score of the appropriate player
    # returns True if a goal was scored, False otherwise
    def check_goal(self) -> None:
        if self.ball.x < 0:
            self.update_player_score(self.player2.id)
            print("Goal scored by player 2")
            return True
        elif self.ball.x > FIELD_DEPTH:
            self.update_player_score(self.player1.id)
            print("Goal scored by player 1")
            return True
        else:
            return False

    # update_game_state method
    # updates the state of the game for the next frame
    # including updating the ball's position, handling collisions, and checking for goals
    # and increments the rally_timer
    async def update_game_state(self) -> None:
        self.current_rally += 1
        await self.send_game_state_to_client()
        await asyncio.sleep(0.1)
        self.ball.update_position()
        self.handle_collisions()

        # self.render()
        # print("ball x: " + str(self.ball.x))
        # print("ball z: " + str(self.ball.z))
        if self.check_goal() == True:
            self.paused = True
    
    # reset_ball method
    # resets the ball to the center of the field
    # and gives it a random direction
    def reset_ball(self):
        if self.ball.x < 0:
            self.ball.direction = random.randrange(-40, 40) #random direction towards player 2 
        elif self.ball.x > FIELD_DEPTH:                             # THIS NEEDS TO BESWAPPED
            self.ball.direction = random.randrange(140, 220)  #random direction towards player 1
        else:
            if random.random() >= .5:
                self.ball.direction = random.randrange(-12, 12)
            else:
                self.ball.direction = random.randrange(168, 192)
        self.ball.position = BALL_DEFAULT_X, 0, BALL_DEFAULT_Z

    # run_rally method
    # runs a rally of the game
    # updates the game state until a goal is scored
    # then updates ball_position for 60 frames as ball goes through the goal
    # updates the longest rally if necessary
    # resets the current rally timer
    async def run_rally(self) -> None: # reset ball position in this method? receive new angle as argument?
        self.reset_ball()
        logging.info("Rally started")
        self.paused = False
        while self.paused == False:
            await self.update_game_state()
        # for counter in range(60):
        #     self.ball.update_position()
        if self.current_rally > self.longest_rally:
            self.longest_rally = self.current_rally
        self.current_rally = 0
    
    # is_game_over method
    # returns True if the game is over, False otherwise
    def is_game_over(self) -> bool:
        return self.time_remaining <= 0 or self.player1.score >= 10 or self.player2.score >= 10 

        
    # end_game method
    # ends the game and sends game stats to server and clients
    # closes the game session
    def end_game(self):
        if (self.player1.score > self.player2.score):
            winner = self.player1.id
        else:
            winner = self.player2.id
        json_data = {
            "game_id": self.game_id,
            "player1_id": self.player1.id,
            "player2_id": self.player2.id,
            "winner": winner,
            "player1_score": self.player1.score,
            "player2_score": self.player2.score,
            "total_hits": self.player1.hits + self.player2.hits,
            "longest_rally": self._longest_rally,
            "game_duration": GAME_DURATION - self.time_remaining
        }
        # send data to clients
        # send data to server
