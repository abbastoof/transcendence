import socketio
from game_logic.entities.gamestate import GameState
from game_logic.entities.player import Player
from game_logic.game_defaults import *
from game_logic.entities.ball import Ball
import logging
import asyncio
import json
import time

# Define custom logging configuration
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.StreamHandler',
        },
        'uvicorn_access': {
            'level': 'ERROR',  # Set to ERROR to suppress lower-level logs
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
        },
        'uvicorn.access': {
            'handlers': ['uvicorn_access'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
}

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",  # Specify allowed origins
    logger=False,              # Disable Socket.IO logging
    engineio_logger=False      # Disable engineio logging
)
app = socketio.ASGIApp(sio)

active_games = {}
sid_to_game = {}

class PongGame:
    def __init__(self, game_id, player1_id, player2_id, is_remote):
        self.game_id = game_id
        self.game_state = self.init_game(game_id, player1_id, player2_id)
        self.sids = []
        self.is_remote = is_remote
        logging.info("Pongstructor")

    def init_game(self, game_id: int, player1_id: int, player2_id: int) -> GameState:
        player1 = Player(player1_id, PLAYER1_START_X)
        player2 = Player(player2_id, PLAYER2_START_X)
        ball = Ball(BALL_DEFAULT_X, BALL_DEFAULT_Z, BALL_RADIUS, BALL_SPEED, BALL_DEFAULT_DIRECTION)
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
                await asyncio.sleep(0.016)  # Adjust this to control the speed of the animation
            await self.post_rally_animation()
            if self.game_state.current_rally > self.game_state.longest_rally:
                self.game_state.longest_rally = self.game_state.current_rally
            self.game_state.in_progress = not self.game_state.is_game_over()
            await asyncio.sleep(0.016)
    
    async def run_game(self, sid) -> None:
        self.sid = sid
        await self.game_loop()
        await self.end_game()

    async def send_initial_game_state(self):
        await sio.emit(
            'send_game_state',
            {
                'type': 'send_game_state',
                'game_id': self.game_state.game_id,
                'ball': {
                    'x': self.game_state.ball.x,
                    'y': self.game_state.ball.y,
                    'z': self.game_state.ball.z,
                },
                'player1_position': {
                    'x': self.game_state.player1.paddle.x,
                    'z': self.game_state.player1.paddle.z,
                },
                'player2_position': {
                    'x': self.game_state.player2.paddle.x,
                    'z': self.game_state.player2.paddle.z,
                },
            },
            room=self.sid
        )

    async def update_game_state(self):
        self.game_state.ball.update_position()
        self.game_state.handle_collisions()
        self.game_state.current_rally += 1
        if self.game_state.check_goal():
            self.game_state.paused = True

        await sio.emit(
            'send_game_state',
            {
                'type': 'send_game_state',
                'game_id': self.game_state.game_id,
                'ball': {
                    'x': self.game_state.ball.x,
                    'y': self.game_state.ball.y,
                    'z': self.game_state.ball.z,
                },
                'player1_position': {
                    'x': self.game_state.player1.paddle.x,
                    'z': self.game_state.player1.paddle.z,
                },
                'player2_position': {
                    'x': self.game_state.player2.paddle.x,
                    'z': self.game_state.player2.paddle.z,
                },
            },
            room=self.sid   
        )

    async def end_game(self):
        if self.game_state.player1.score > self.game_state.player2.score:
            winner = self.game_state.player1.id
        else:
            winner = self.game_state.player2.id
        json_data = {
            "type": "game_over",
            "game_id": self.game_state.game_id,
            "player1_id": self.game_state.player1.id,
            "player2_id": self.game_state.player2.id,
            "winner": winner,
            "player1_score": self.game_state.player1.score,
            "player2_score": self.game_state.player2.score,
            "total_hits": self.game_state.player1.hits + self.game_state.player2.hits,
            "longest_rally": self.game_state.longest_rally,
            "game_duration": GAME_DURATION - self.game_state.time_remaining
        }
        await sio.emit('game_over', json_data, room=self.sid)
        #logging.info("Game over")

    async def post_rally_animation(self):
        for _ in range(40):  # Adjust the range to control the duration of the animation
            self.game_state.ball.update_position()
            await sio.emit(
                'send_game_state',
                {
                    'type': 'send_game_state',
                    'game_id': self.game_id,
                    'ball': {
                        'x': self.game_state.ball.x,
                        'y': self.game_state.ball.y,
                        'z': self.game_state.ball.z,
                    },
                    'player1_position': {
                        'x': self.game_state.player1.paddle.x,
                        'z': self.game_state.player1.paddle.z,
                    },
                    'player2_position': {
                        'x': self.game_state.player2.paddle.x,
                        'z': self.game_state.player2.paddle.z,
                    },
                },
                room=self.sid
            )
            await asyncio.sleep(0.016)  # Adjust this to control the speed of the animation

    async def handle_paddle_movement(self, sid, data):
        start_time = time.time()
        # Check if 'data' is a string and attempt to parse it
        if isinstance(data, str):
            try:
                data = json.loads(data)  # Parse the JSON string into a dictionary
            except json.JSONDecodeError:
                logging.error("Received data is not valid JSON")
                return

        if not isinstance(data, dict):  # Ensure data is a dictionary
            logging.error("Received data is not a dictionary")
            return

        if not hasattr(self, 'game_state'):
            logging.error("Game state is not initialized")
            return

        event_type = data.get('type')

        if event_type == 'move_paddle':
            game_id = data.get('game_id')
            if game_id != self.game_state.game_id:
                logging.error("Game ID does not match")
                return
            player1_id = data.get('player1_id')
            p1_delta_z = data.get('p1_delta_z')
            player2_id = data.get('player2_id')
            p2_delta_z = data.get('p2_delta_z')
            logging.info(f"Player1: {player1_id}, Delta Z: {p1_delta_z}")
            logging.info(f"Player2: {player2_id}, Delta Z: {p2_delta_z}")
            if player1_id is not None and p1_delta_z is not None:
                self.game_state.move_player(player1_id, p1_delta_z)
            
            if player2_id is not None and p2_delta_z is not None:
                self.game_state.move_player(player2_id, p2_delta_z)
            
            # await self.update_game_state()
            logging.info("Paddle moved")
        #end_time = time.time()
        #logging.info(f"handle_paddle_movement execution time: {end_time - start_time} seconds")
        

@sio.event
async def connect(sid, environ):
    logging.info(f'Client connected: {sid}, Path: {environ.get("PATH_INFO")}')

@sio.event
async def disconnect(sid):
    logging.info(f'Disconnect: {sid}')
    if sid in sid_to_game:
        game_id = sid_to_game.pop(sid)
        if game_id in active_games:
            game_instance = active_games[game_id]
            if sid in game_instance.sids:
                game_instance.sids.remove(sid)
                if not game_instance.sids:
                    del active_games[game_id]  # Optionally handle cleanup if no players are left


@sio.event
async def message(sid, data):
    logging.info(f"Message received from {sid}: {data}")

@sio.event
async def start_game(sid, data):
    # Handle the start_game message
    logging.info(f"Start game request from {sid}: {data}")
    required_keys = ['game_id', 'player1_id', 'player2_id', 'is_remote']
    for key in required_keys:
        if key not in data:
            logging.info(f"Missing key in data: {key}")
            await sio.emit('error', {'message': f'Missing key: {key}'}, room=sid)
            return
    game_id = data.get('game_id')
    player1_id = data.get('player1_id')
    player2_id = data.get('player2_id')
    is_remote = data.get('is_remote')
    logging.info(f"Got game_id: {game_id}, player1_id: {player1_id}, player2_id: {player2_id}, is_remote: {is_remote}")
    # Validate data
    if not all([game_id, player1_id, player2_id]) or is_remote is None:
        await sio.emit('error', {'message': 'Invalid game initialization data'}, room=sid)
        return

    # Check if the game_id is already in use
    if game_id in active_games:
        await sio.emit('error', {'message': 'Game ID already in use'}, room=sid)
        return

    # Create a new game instance
    game_instance = PongGame(game_id, player1_id, player2_id, is_remote)
    active_games[game_id] = game_instance  # Track game instance by game_id
    game_instance.sids = [sid]  # Initialize with the current session id
    sid_to_game[sid] = game_id
    
    try:
        asyncio.create_task(game_instance.run_game(sid))
        logging.info("Game started")
    except Exception as e:
        logging.error(f"Error starting game: {e}")
        await sio.emit('error', {'message': 'Error starting game'}, room=sid)

@sio.event
async def move_paddle(sid, data):
    game_id = sid_to_game.get(sid)
    if game_id in active_games:
        game_instance = active_games[game_id]
        await game_instance.handle_paddle_movement(sid, data)
    else:
        logging.error(f"No active game instance for sid: {sid}")


@sio.event
async def test(sid):
    await sio.emit('test', {'message': 'Test message'}, room=sid)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8010, log_level="info", log_config=logging_config)