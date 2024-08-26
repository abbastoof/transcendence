import socketio
import time
import json
import logging
import socketio
import os

# Define a dictionary to store active game instances
active_games = {}

# This will hold all the pendind game requests
remote_game_requests = []

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

HOSTNAME = os.environ.get("HOSTNAME")
full_host_url = f"https://{HOSTNAME}:3000"

# Create a new ASGI application using the Socket.IO server
# The 'async_mode' parameter is set to 'asgi' to use the ASGI server
# The 'cors_allowed_origins' parameter is set to '*' to allow all origins (this needs to be eventually restricted)
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins= full_host_url,
    logger=False,              # Disable Socket.IO logging
    engineio_logger=False,      # Disable engineio logging
    ping_interval=10,
    ping_timeout=5
)
# Create an ASGI application using the Socket.IO server
# This application can be run using an ASGI server such as Uvicorn
app = socketio.ASGIApp(sio)


# Define a dictionary to store the game instance associated with each session ID
sid_to_game = {}


class GameRequest:
    def __init__(self, sid, game_id: int, player1_id, player2_id, is_remote):
        self.time_stamp = time.time()
        self.game_id = game_id
        self.sid = sid
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.is_remote = is_remote

    async def has_timed_out(self):
        curr_time = time.time()
        if (curr_time - self.time_stamp) > 10.0:
            logging.info("Request game has timed out, sending cancel_game!\n")
            json_data = {
                    "type": "cancel_game",
                    "gameId": self.game_id,
                    }
            await sio.emit('cancel_game', json_data, room=self.sid)
            return True
        return False

    def is_a_match(self, game_id, player1_id, player2_id):
        if (
                self.game_id == game_id and
                self.player1_id == player1_id and
                self.player2_id == player2_id
            ):
            return True
        else:
            return False

def coupled_request(game_id, player1_id, player2_id):
    for instance in remote_game_requests:
        if instance.is_a_match(game_id, player1_id, player2_id):
            remote_game_requests.remove(instance)
            return instance
    return None


#Function Validates the data received from the frontend before the start of the game
async def validate_data(data):
    # List of required keys
    required_keys = ['game_id', 'player1_id', 'player2_id', 'is_remote']

    # Check for missing keys
    for key in required_keys:
        if key not in data:
            logging.info(f"Missing key in data: {key}")
            await sio.emit('error', {'message': f'Missing key: {key}'}, room=sid)
            return False
    # Extract values
    game_id = data.get('game_id')
    player1_id = data.get('player1_id')
    player2_id = data.get('player2_id')
    is_remote = data.get('is_remote')

    # Log extracted values
    logging.info(f"Got game_id: {game_id},\
                    player1_id: {player1_id}, \
                    player2_id: {player2_id}, \
                    is_remote: {is_remote}")

    # Validate extracted values
    if not all([game_id, player1_id, player2_id]) or is_remote is None:
        await sio.emit('error', {'message': 'Invalid game initialization data'}, room=sid)
        logging.error("Invalid game initialization data")
        return

    # Check if the game_id is already in use
    if game_id in active_games:
        await sio.emit('error', {'message': 'Game ID already in use'}, room=sid)
        logging.error(f"Game ID {game_id} already in use")
        return
    return True
