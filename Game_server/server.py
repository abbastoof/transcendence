# server.py

import socketio
from game_logic.entities.gamestate import GameState
from game_logic.entities.player import Player
from game_logic.game_defaults import *
from game_logic.entities.ball import Ball
import logging

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=["http://localhost:5173"])
app = socketio.ASGIApp(sio)

class PongGame:
    def __init__(self, game_id, player1_id, player2_id):
        self.game_state = self.init_game(game_id, player1_id, player2_id)

    def init_game(self, game_id: int, player1_id: int, player2_id: int) -> GameState:
        # Create the players
        player1 = Player(player1_id, PLAYER1_START_X)
        player2 = Player(player2_id, PLAYER2_START_X)
        
        # Create the ball
        ball = Ball(BALL_DEFAULT_X, BALL_DEFAULT_Z, BALL_RADIUS, BALL_SPEED, BALL_DEFAULT_DIRECTION)
        # Create the game state
        game_state = GameState(game_id, player1, player2, ball)
        
        return game_state

    async def game_loop(self) -> None:
        while self.game_state.in_progress:
            self.game_state.current_rally = 0
            self.game_state.reset_ball()
            logging.info("Rally started")
            await self.send_initial_game_state()
            self.game_state.paused = False
            while not self.game_state.paused:
                await self.update_game_state()
            await self.post_rally_animation()
            if self.game_state.current_rally > self.game_state.longest_rally:
                self.game_state.longest_rally = self.game_state.current_rally
    
    async def run_game(self) -> None:
        await self.game_loop()
        self.end_game()

game = PongGame(1, 1, 2)

@sio.event
async def connect(sid, environ):
    print('connect ', sid)
    await game.run_game()

@sio.event
async def disconnect(sid):
    print('disconnect ', sid)

@sio.event
async def message(sid, data):
    print('message ', data)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8011)