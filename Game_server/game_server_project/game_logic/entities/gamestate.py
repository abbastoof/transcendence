from channels.layers import get_channel_layer
from game_logic.entities.player import Player
from game_logic.entities.ball import Ball
from game_logic.game_defaults import *
import random
import time

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
            raise ValueError("Invalid player ID")

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
        if self.ball.z <= 0 or self.ball.z >= FIELD_WIDTH:
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
        if self.ball.x > FIELD_DEPTH:
            self.update_player_score(self.player1.id)
            print("Goal scored by player 1")
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
    def update_game_state(self) -> None:
        self.current_rally += 1
        self.ball.update_position()
        self.handle_collisions()
        self.render()
        # print("ball x: " + str(self.ball.x))
        # print("ball z: " + str(self.ball.z))
        if self.check_goal() == True:
            self.paused = True
    
    def render(self) -> None:
        start_time = time.time()
        # Clear the terminal screen
        print('\033c', end='')

        # Create a 2D array for the game field that fits the terminal window
        field = [[' ' for _ in range(160)] for _ in range(40)]

        # Set the ball and paddles in the field, scaling down their positions to fit the terminal window
        ball_z = 39 - int(self._ball.z * 40 / FIELD_WIDTH)  # Invert the ball's z-position
        ball_x = int(self._ball.x * 160 / FIELD_DEPTH)
        if 0 <= ball_z < 40 and 0 <= ball_x < 160:
            field[ball_z][ball_x] = 'O'
        # Correctly calculate the top and bottom positions of paddle1
        paddle1_top = 39 - int(self._player1.paddle.z * 40 / FIELD_WIDTH - self._player1.paddle.width * 40 / FIELD_WIDTH / 2)
        paddle1_bottom = 39 - int(self._player1.paddle.z * 40 / FIELD_DEPTH + self._player1.paddle.width * 40 / FIELD_WIDTH / 2)
        # Ensure the loop correctly iterates from bottom to top for paddle1
        for z in range(paddle1_bottom, paddle1_top + 1):  # Include paddle1_top in the range
            if 0 <= z < 40:
                field[z][0] = '|'

        # Correctly calculate the top and bottom positions of paddle2
        paddle2_top = 39 - int(self._player2.paddle.z * 40 / FIELD_WIDTH - self._player2.paddle.width * 40 / FIELD_WIDTH / 2)
        paddle2_bottom = 39 - int(self._player2.paddle.z * 40 / FIELD_WIDTH + self._player2.paddle.width * 40 / FIELD_WIDTH / 2)
        # Ensure the loop correctly iterates from bottom to top for paddle2
        for z in range(paddle2_bottom, paddle2_top + 1):  # Include paddle2_top in the range
            if 0 <= z < 40:
                field[z][159] = '|'

        # Print the field
        print('+', '-' * 160, '+', sep='')
        for row in field:
            print(' ', ''.join(row), ' ', sep='')
        print('+', '-' * 160, '+', sep='')

        # Print the game state information
        print(f"Game ID: {self.game_id}")
        print(f"Current Rally: {self.current_rally}")
        print(f"Longest Rally: {self.longest_rally}")
        print(f"Ball direction: {self.ball.direction}")
        print(f"Ball speed: {self.ball.speed}")
        print(f"Ball delta x: {self.ball.delta_x}")
        print(f"Ball delta z: {self.ball.delta_z}")
        print(f"Ball pos: {self.ball.x}, {self.ball.z}")
        print(f"Game Paused: {self._paused}")
        print(f"Game In Progress: {self._in_progress}")
        print(f"Player1 hits: {self.player1.hits}")
        print(f"Player2 hits: {self.player2.hits}")
        frame_time = time.time() - start_time
        if frame_time < 1/60:
            time.sleep(1/60 - frame_time)
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
    def run_rally(self) -> None: # reset ball position in this method? receive new angle as argument?
        self.reset_ball()
        self.paused = False
        while self.paused == False:
            self.update_game_state()
        # for counter in range(60):
        #     self.ball.update_position()
        if self.current_rally > self.longest_rally:
            self.longest_rally = self.current_rally
        self.current_rally = 0
    
    # is_game_over method
    # returns True if the game is over, False otherwise
    def is_game_over(self) -> bool:
        return self.time_remaining <= 0 or self.player1.score >= 10 or self.player2.score >= 10 

    # def reset_game(self):
        # self.player1.score = 0
        # self.player1.score = 0
        # self.ball.reset()
        # self.ball.direction(default direction)

    # def handle_input(self, input)

    async def send_game_state_to_client(self):
        json_data = {
            "game_id": self.game_id,
            "player1": {
                "id": self.player1.id,
                "score": self.player1.score,
                "x": self.player1.paddle.x,
                "y": self.player1.paddle.y,
                "z": self.player1.paddle.z
            },
            "player2_pos": {
                "id": self.player2.id,
                "score": self.player2.score,
                "x": self.player2.paddle.x,
                "y": self.player2.paddle.y,
                "z": self.player2.paddle.z
            },
            "ball": {
                "pos": {
                    "x": self.ball.x,
                    "y": self.ball.y,
                    "z": self.ball.z
                },
                "delta": {
                    "x": self.ball.delta_x,
                    "z": self.ball.delta_z
                },
            },
            "time_remaining": self.time_remaining,
        }
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"game_{self.game_id}",
            {
                "type": "game_state",
                "text": json_data
            }
        )

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
