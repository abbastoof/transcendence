import socketio
from game_logic.entities.gamestate import GameState
from game_logic.entities.player import Player
from game_logic.game_defaults import *
from game_logic.entities.ball import Ball
import logging
import asyncio
import json

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

# Create a new ASGI application using the Socket.IO server
# The 'async_mode' parameter is set to 'asgi' to use the ASGI server
# The 'cors_allowed_origins' parameter is set to '*' to allow all origins (this needs to be eventually restricted)
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",  # Specify allowed origins
    logger=False,              # Disable Socket.IO logging
    engineio_logger=False      # Disable engineio logging
)
# Create an ASGI application using the Socket.IO server
# This application can be run using an ASGI server such as Uvicorn
app = socketio.ASGIApp(sio)

# Define a dictionary to store active game instances
active_games = {}

# Define a dictionary to store the game instance associated with each session ID
sid_to_game = {}

# PongGame class
# Represents a game of Pong
# Properties:
#   - game_id: the ID of the game
#   - game_state: the game state object
#   - sids: a list of session IDs of the clients connected to the game
#   - is_remote: a boolean indicating whether the game is remote or local
class PongGame:
    def __init__(self, game_id, player1_id, player2_id, is_remote):
        self.game_id = game_id
        self.game_state = self.init_game(game_id, player1_id, player2_id)
        self.sids = []
        self.sid_to_player_id = {}
        self.is_remote = is_remote
        logging.info("Pongstructor")

    # init_game method
    # Initializes the game state
    # Parameters:
    #   - game_id: the ID of the game
    #   - player1_id: the ID of player 1
    #   - player2_id: the ID of player 2
    # Returns:
    #   - a new GameState object
    # The game state is initialized with the given game ID, player IDs, and default values
    # The player positions are set to the default starting positions
    # The ball is placed at the default starting position
    # The game state is returned
    # The game state is responsible for updating the game state and sending the updated state to the client
    def init_game(self, game_id: int, player1_id: int, player2_id: int) -> GameState:
        player1 = Player(player1_id, PLAYER1_START_X)
        player2 = Player(player2_id, PLAYER2_START_X)
        ball = Ball(BALL_DEFAULT_X, BALL_DEFAULT_Z, BALL_RADIUS, BALL_SPEED, BALL_DEFAULT_DIRECTION)
        game_state = GameState(game_id, player1, player2, ball)
        return game_state

    # add_player method
    # Adds a player session to the game
    async def add_player(self, sid, player_id):
        self.sids.append(sid)
        if self.is_remote:
            self.sid_to_player_id[sid] = player_id
        logging.info(f"Player {sid} added to game {self.game_id}")

    # remove_player method
    # Removes a player session from the game
    async def remove_player(self, sid):
        if sid in self.sids:
            self.sids.remove(sid)
            player_id = self.sid_to_player_id.pop(sid, None)
            logging.info(f"Player {player_id} (sid: {sid}) removed from game {self.game_id}")
     
    # game_loop method
    # Runs the game loop
    # The game loop runs until the game is over
    # The game loop updates the game state and sends the updated state to the client
    # When goal is scored, the game is paused and the score is sent to the clients
    # and the post-rally animation is run
    # If game is not over, the game continues
    async def game_loop(self) -> None:
        while self.game_state.in_progress:
            self.game_state.current_rally = 0
            self.game_state.reset_ball()
            logging.info(f"Rally started, game ID: {self.game_state.game_id}, sids: {self.sids}")
            await self.send_game_state_to_client()
            await asyncio.sleep(0.5) # Little break before start of the rally
            self.game_state.paused = False
            while not self.game_state.paused:
                await self.update_game_state()
                await asyncio.sleep(0.016)  # Adjust this to control the speed of the animation
            await self.send_score()
            await self.post_rally_animation()
            if self.game_state.current_rally > self.game_state.longest_rally:
                self.game_state.longest_rally = self.game_state.current_rally
            self.game_state.in_progress = not self.game_state.is_game_over()
    
    # run_game method
    # Runs the game loop
    # When game loop is over, calls for end_game method
    async def run_game(self) -> None:
        await self.game_loop()
        await self.end_game()

    # update_game_state method
    # Updates the game state
    # The ball position is updated
    # Collisions are handled
    # The current rally is incremented
    # If a goal is scored, the game is paused
    # The updated game state is sent to the client
    async def update_game_state(self):
        self.game_state.ball.update_position()
        self.game_state.handle_collisions()
        self.game_state.current_rally += 1
        if self.game_state.check_goal():
            self.game_state.paused = True
        await self.send_game_state_to_client()
 
    # send_game_state_to_client method
    # Sends the game state to the client
    # The game state is sent as a JSON object
    # The JSON object contains the game ID, ball position, and player positions
    # The JSON object is sent to each client session ID in
    # the game instance's sids list
    async def send_game_state_to_client(self):
        game_state_data = {
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
        for sid in self.sids:
            await sio.emit('send_game_state', game_state_data, room=sid)

    # end_game method
    # Ends the game
    # The winner is determined based on the player scores
    # The game over message is sent to the clients with the game stats
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
        for sid in self.sids:
            await sio.emit('game_over', json_data, room=sid)
        #logging.info("Game over")

    # post_rally_animation method
    # Runs the post-rally animation (aka ball going through the goal)
    # The ball position is updated for 40 frames
    # The updated game state is sent to the clients each frame
    async def post_rally_animation(self):
        for _ in range(40):  # Adjust the range to control the duration of the animation
            self.game_state.ball.update_position()
            await self.send_game_state_to_client()
            await asyncio.sleep(0.016)  # Adjust this to control the speed of the animation
    
    # send_score method
    # Sends the player scores to the clients
    # The player scores are sent as a JSON object
    async def send_score(self):
        data = {
            'type': 'score',
            'game_id': self.game_state.game_id,
            'player1_score': self.game_state.player1.score,
            'player2_score': self.game_state.player2.score,
        }
        for sid in self.sids:
            await sio.emit('score', data, room=sid)

    # handle_paddle_movement method
    # Handles paddle movement
    # The 'data' parameter is a dictionary containing the paddle movement data
    async def handle_paddle_movement(self, sid, data):
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
                        # Handle local and remote games differently
            if self.is_remote:
                # Remote game: Use sid to player ID mapping
                player_id = self.sid_to_player_id.get(sid)
                if not player_id:
                    logging.error(f"No player ID associated with sid: {sid}")
                    return
                
                p_delta_z = data.get('delta_z')
                if player_id == self.game_state.player1.id:
                    self.game_state.move_player(player_id, p_delta_z)
                elif player_id == self.game_state.player2.id:
                    self.game_state.move_player(player_id, p_delta_z)
                else:
                    logging.error(f"Player ID {player_id} not found in game state")
            else:
                player1_id = data.get('player1_id')
                p1_delta_z = data.get('p1_delta_z')
                player2_id = data.get('player2_id')
                p2_delta_z = data.get('p2_delta_z')
                if player1_id is not None and p1_delta_z is not None:
                    self.game_state.move_player(player1_id, p1_delta_z)
                
                if player2_id is not None and p2_delta_z is not None:
                    self.game_state.move_player(player2_id, p2_delta_z)


# Event handler for new connections
# This function is called when a new client connects to the server
# The 'sid' parameter is the session ID of the client
# The 'environ' parameter contains information about the connection
# such as the path, headers, and query parameters
@sio.event
async def connect(sid, environ):
    logging.info(f'Client connected: {sid}, Path: {environ.get("PATH_INFO")}')

# Event handler for disconnections
# This function is called when a client disconnects from the server
# The 'sid' parameter is the session ID of the client
# Removes sid from sid_to_game and active_games
# If no players are left in the game, the game instance is or should be removed
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
                    logging.info(f"No players left in game {game_id}") 
                    del active_games[game_id]  # this cleanup actually does not work

# Event handler for messages
# This function is called when a client sends a message to the server
# Logs the message, doesnt do anything else
@sio.event
async def message(sid, data):
    logging.info(f"Message received from {sid}: {data}")

# Event handler for start_game message
# This function is called when a client sends a start_game message to the server
# The 'data' parameter is a dictionary containing the game initialization data
# The 'sid' parameter is the session ID of the client
# The function validates the game initialization data and creates a new game instance
# The game instance is started in a separate task
# Currently this only handles the local game
@sio.event
async def start_game(sid, data):
    # Log the received data
    logging.info(f"Start game request from {sid}: {data}")
    
    # List of required keys
    required_keys = ['game_id', 'player1_id', 'player2_id', 'is_remote']
    
    # Check for missing keys
    for key in required_keys:
        if key not in data:
            logging.info(f"Missing key in data: {key}")
            await sio.emit('error', {'message': f'Missing key: {key}'}, room=sid)
            return
    
    # Extract values
    game_id = data.get('game_id')
    player1_id = data.get('player1_id')
    player2_id = data.get('player2_id')
    is_remote = data.get('is_remote')

    # Log extracted values
    logging.info(f"Got game_id: {game_id}, player1_id: {player1_id}, player2_id: {player2_id}, is_remote: {is_remote}")
    
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

    # Create a new game instance
    try:
        game_instance = PongGame(game_id, player1_id, player2_id, is_remote)
        active_games[game_id] = game_instance  # Track game instance by game_id
        game_instance.sids = [sid]  # Initialize with the current session id
        sid_to_game[sid] = game_id
        
        # Start the game in a separate task
        asyncio.create_task(game_instance.run_game())
        logging.info("Game started")
    except Exception as e:
        logging.error(f"Error starting game: {e}")
        await sio.emit('error', {'message': 'Error starting game'}, room=sid)

# Event handler for move_paddle message
# This function is called when a client sends a move_paddle message to the server
# The 'data' parameter is a dictionary containing the paddle movement data
# The 'sid' parameter is the session ID of the client
# The function retrieves the game instance associated with the session ID
# and calls the handle_paddle_movement method on the game instance
# If no active game instance is found, an error message is logged
# The game instance is responsible for updating the game state and sending the updated state to the client
# The game state is updated in a separate task to avoid blocking the event loop
@sio.event
async def move_paddle(sid, data):
    game_id = sid_to_game.get(sid)
    if game_id in active_games:
        game_instance = active_games[game_id]
        await game_instance.handle_paddle_movement(sid, data)
    else:
        logging.error(f"No active game instance for sid: {sid}")

# Event handler for test message
# This function is called when a client sends a test message to the server
@sio.event
async def test(sid):
    await sio.emit('test', {'message': 'Test message'}, room=sid)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8010, log_level="info", log_config=logging_config)