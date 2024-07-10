from entities.gamestate import GameState
from entities.player import Player
from game_defaults import *
from entities.ball import Ball
import logging

def main():
    logging.basicConfig(filename='bong.log', level=logging.INFO)
    run_game(1, 1, 2)

def init_game(game_id: int, player1_id: int, player2_id: int) -> GameState:
    # Create the players
    player1 = Player(player1_id, PLAYER1_START_X)
    player2 = Player(player2_id, PLAYER2_START_X)
    
    # Create the ball
    ball = Ball(BALL_DEFAULT_X, BALL_DEFAULT_Z, BALL_RADIUS, BALL_SPEED, BALL_DEFAULT_DIRECTION)
    # Create the game state
    game_state = GameState(game_id, player1, player2, ball)
    
    return game_state

def game_loop(game_state: GameState) -> None:
    while game_state.in_progress:
        game_state.run_rally()
        game_state.in_progress = not game_state.is_game_over()

def run_game(game_id, player1_id, player2_id) -> None:
    game_state = init_game(game_id, player1_id, player2_id)
    game_loop(game_state)
    game_state.end_game()

if __name__ == "__main__":
    main()