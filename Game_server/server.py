import socketio
from game_logic.entities.gamestate import GameState
from game_logic.entities.player import Player
from game_logic.game_defaults import *
from game_logic.entities.ball import Ball
import asyncio
import threading
import json
import os
import requests
import uvicorn 
from server_utils import *

TOEKNSERVICE = os.environ.get('TOKEN_SERVICE')

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
        self.game_loop_task = None
        self.is_remote = is_remote
        self.is_quit = False

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

    # remove_player method
    # Removes a player session from the game
    async def remove_player(self, sid):
        if sid in self.sids:
            self.sids.remove(sid)
            player_id = self.sid_to_player_id.pop(sid, None)
     
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
            await self.send_game_state_to_client()
            await asyncio.sleep(1.0) # Little break before start of the rally
            self.game_state.paused = False
            while not self.game_state.paused:
                await self.update_game_state()
                await asyncio.sleep(0.016)  # Adjust this to control the speed of the animation
            if self.game_state.current_rally > self.game_state.longest_rally:
                self.game_state.longest_rally = self.game_state.current_rally
            await self.send_score()
            await self.post_rally_animation()
            if self.game_state.is_game_over():
                self.game_state.in_progress = False
                break  # Ensure the loop exits once the game is over


    # run_game method
    # Runs the game loop
    # When game loop is over, calls for end_game method
    async def run_game(self) -> None:
        for sid in self.sids:
            await sio.emit('game_start', {'type': 'game_start', 'gameId': self.game_id}, room=sid)
        await asyncio.sleep(1.0)
        self.game_loop_task = asyncio.create_task(self.game_loop())
        # Wait for the game loop to finish
        await self.game_loop_task
        # Call end_game after the
        await self.end_game()

    # update_game_state method
    # Updates the game state
    # The ball position is updated
    # Collisions are handled
    # The current rally is incremented
    # If a goal is scored, the game is paused
    # The updated game state is sent to the client
    async def update_game_state(self):
        self.game_state.current_rally += 1
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
            'gameId': self.game_state.game_id,
            'ballPosition': {
                'x': self.game_state.ball.x,
                'y': self.game_state.ball.y,
                'z': self.game_state.ball.z,       
            },
            'ballDelta': {
                'dx': self.game_state.ball.delta_x,
                'dz': self.game_state.ball.delta_z,
            },
            'player1Pos': {
                'x': self.game_state.player1.paddle.x,
                'z': self.game_state.player1.paddle.z,
            },
            'player2Pos': {
                'x': self.game_state.player2.paddle.x,
                'z': self.game_state.player2.paddle.z,
            },
            'bounce' : self.game_state.bounce,
            'hitpos' : self.game_state.hitpos,
            'paused': self.game_state.paused,
        }
        for sid in self.sids:
            await sio.emit('send_game_state', game_state_data, room=sid)

    # end_game method
    # Ends the game
    # The winner is determined based on the player scores
    # The game over message is sent to the clients with the game stats
    async def end_game(self):
        self.game_state.in_progress = False
        if self.game_loop_task is not None:
            if not self.game_loop_task.done():
                self.game_loop_task.cancel()
            try:
                await self.game_loop_task  # Await to handle cancellation gracefully
            except asyncio.CancelledError:
                logging.info(f"Game loop for game {self.game_state.game_id} was cancelled.")
        else:
            logging.warning("Game loop task is None; cannot await a non-existent task.")
        
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
            "player1_hits": self.game_state.player1.hits,
            "player2_hits": self.game_state.player2.hits,
            "longest_rally": self.game_state.longest_rally,
            "game_duration": GAME_DURATION - self.game_state.time_remaining
        }
        for sid in self.sids:
            await sio.emit('game_over', json_data, room=sid)
        self.sids.clear()  # Clear all session IDs from the game instance
        del active_games[self.game_id]  # Remove the game instance from the active games
        del self.game_state  # If possible, clear the game state
        print_active_games()
        

    # post_rally_animation method
    # Runs the post-rally animation (aka ball going through the goal)
    # The ball position is updated for 40 frames
    # The updated game state is sent to the clients each frame
    async def post_rally_animation(self):
        for _ in range(60):  # Adjust the range to control the duration of the animation
            self.game_state.ball.update_position()
            await self.send_game_state_to_client()
            await asyncio.sleep(0.016)  # Adjust this to control the speed of the animation
    
    # send_score method
    # Sends the player scores to the clients
    # The player scores are sent as a JSON object
    async def send_score(self):
        data = {
            'type': 'score',
            'gameId': self.game_state.game_id,
            'player1Score': self.game_state.player1.score,
            'player2Score': self.game_state.player2.score,
        }
        for sid in self.sids:
            await sio.emit('score', data, room=sid)
 
    async def cancel_game(self):
        # Mark the game as not in progress
        self.game_state.in_progress = False

        # Cancel the game loop task if it's running
        if self.game_loop_task is not None and not self.game_loop_task.done():
            self.game_loop_task.cancel()
            try:
                await self.game_loop_task  # Await to handle cancellation gracefully
            except asyncio.CancelledError:
                logging.info(f"Game loop for game {self.game_state.game_id} was cancelled.")
            except Exception as e:
                logging.error(f"Error while awaiting game loop cancellation: {e}")

        # Notify all connected clients about the cancellation
        data = {
            'type': 'cancel_game',
            'gameId': self.game_state.game_id,
            'message': 'Game has been cancelled',
        }
        for sid in self.sids:
            try:
                await sio.emit('cancel_game', data, room=sid)
            except Exception as e:
                logging.error(f"Error sending cancel_game message to {sid}: {e}")

        # Clear all session IDs from the game instance
        self.sids.clear()

        # Remove the game instance from the active games
        if self.game_id in active_games:
            del active_games[self.game_id]

        # Clear the game state if possible
        self.game_state = None

    # handle_paddle_movement method
    # Handles paddle movement
    # The 'data' parameter is a dictionary containing the paddle movement data
    async def handle_paddle_movement(self, sid, data):

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
                player_id = data.get("player_id")
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
        await self.send_game_state_to_client()

def print_active_games():
    if active_games:
        logging.info("List of active games:")
        for game_id, game_instance in active_games.items():
            logging.info(f"Game ID: {game_id}, Players: {game_instance.game_state.player1.id} vs {game_instance.game_state.player2.id}")
    else:
        logging.info("No active games currently.")

# Event handler for new connections
# This function is called when a new client connects to the server
# The 'sid' parameter is the session ID of the client
# The 'environ' parameter contains information about the connection
# such as the path, headers, and query parameters
@sio.event
async def connect(sid, environ):
    logging.info(f'Client connected: {sid}, Path: {environ.get("PATH_INFO")}')
    json_data = {
        "type": "game_defaults",
        "PADDLE_WIDTH": PADDLE_WIDTH,
        "PADDLE_DEPTH": PADDLE_DEPTH,
        "BALL_RADIUS": BALL_RADIUS,
        "PADDLE_SPEED": PADDLE_SPEED
    }
    await sio.emit('game_defaults', json_data, room=sid)

# Event handler for disconnections
# This function is called when a client disconnects from the server
# The 'sid' parameter is the session ID of the client
# Removes sid from sid_to_game and active_games
# If no players are left in the game, the game instance is or should be removed
@sio.event
async def disconnect(sid):
    logging.info(f'Disconnect: {sid}')
    if sid in sid_to_game:
        game_id = sid_to_game.pop(sid, None)
        if game_id is not None and game_id in active_games:
            game_instance = active_games[game_id]
            if sid in game_instance.sids:
                game_instance.sids.remove(sid)
                if game_instance.is_remote and not game_instance.is_quit and game_instance.sids.__len__() == 1:
                    await game_instance.cancel_game()
                elif game_instance.sids.__len__() == 0:
                    await game_instance.end_game()


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
    
    if await validate_data(data) is False:
        return

    # Extract values
    game_id = data.get('game_id')
    player1_id = data.get('player1_id')
    player2_id = data.get('player2_id')
    is_remote = data.get('is_remote')
    if game_id in active_games:
        await active_games[game_id].end_game()
        del active_games[game_id]
    # Create a new game instance
    try:
        game_instance = PongGame(game_id, player1_id, player2_id, is_remote)
        active_games[game_id] = game_instance  # Track game instance by game_id
        game_instance.sids = [sid]  # Initialize with the current session id
        sid_to_game[sid] = game_id
        
        # Start the game in a separate task
        asyncio.create_task(game_instance.run_game())
    except Exception as e:
        logging.error(f"Error starting game: {e}")
        await sio.emit('error', {'message': 'Error starting game'}, room=sid)


async def start_online_game(p1_sid, p2_sid, game_id, player1_id, player2_id):

    # Create a new game instance
    try:
        game_instance = PongGame(game_id, player1_id, player2_id, True)
        active_games[game_id] = game_instance  # Track game instance by game_id
        game_instance.sids = [p1_sid, p2_sid]  # Initialize with the current session id
        #game_instance.add_player(p1_sid, player1_id)
        #game_instance.add_player(p2_sid, player2_id)
        sid_to_game[p1_sid] = game_id
        sid_to_game[p2_sid] = game_id
        
        # Start the game in a separate task
        asyncio.create_task(game_instance.run_game())
    except Exception as e:
        logging.error(f"Error starting game: {e}")
        await sio.emit('error', {'message': 'Error starting game'}, room=sid)

def validate_token(id, token):
    if token:
        data = {"id" : id, "access" : token, "is_frontend" : True}
        response = requests.post(f"{TOEKNSERVICE}/auth/token/validate-token/", data=data)
        response_data = response.json()
        if "error" not in response_data:
            return True
    return False

@sio.event
async def join_game(sid, data):
    # Log the received data
    
    if await validate_data(data) is False:
        return

    # Extract values
    game_id = data.get('game_id')
    local_player_id = data.get('local_player_id')
    player1_id = data.get('player1_id')
    player2_id = data.get('player2_id')
    is_remote = data.get('is_remote')
    token = data.get('token')

    if validate_token(local_player_id, token) is False:
        await sio.emit('invalid_token', room=sid)
        return
    couple = coupled_request(game_id, player1_id, player2_id)
    if couple is not None:
        if player1_id == local_player_id:
            player1_sid = sid
            player2_sid = couple.sid
        else:
            player1_sid = couple.sid
            player2_sid = sid
        await start_online_game(player1_sid, player2_sid, game_id, player1_id, player2_id)
    else: 
        game_request = GameRequest(sid, game_id, player1_id, player2_id, is_remote)
        remote_game_requests.append(game_request)
        return

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
        await sio.emit('error', {'message': 'No active game instance'}, room=sid)
        logging.error(f"No active game instance for sid: {sid}")

@sio.event
async def quit_game(sid, data):
    logging.info(f"Quit game request from {sid}: {data}")
    
    game_id = data.get('game_id')
    player_id = data.get('player_id')

    if game_id in active_games:
        game_instance = active_games[game_id]
        game_instance.is_quit = True

        # Identify the quitting player and the remaining player
        if game_instance.game_state.player1.id == player_id:
            quitting_player = game_instance.game_state.player1
            remaining_player = game_instance.game_state.player2
        elif game_instance.game_state.player2.id == player_id:
            quitting_player = game_instance.game_state.player2
            remaining_player = game_instance.game_state.player1
        else:
            logging.error(f"Player ID {player_id} not found in game {game_id}")
            return

        # Set the game as over with a default score, e.g., 10-0
        quitting_player.score = 0
        remaining_player.score = 10

        # Notify all players in the session that the game has ended because a player quit
        json_data = {
            "type": "quit_game",
            "gameId": game_id,
            "quittingPlayerId": quitting_player.id,
            "remainingPlayerId": remaining_player.id,
            "quittingPlayerScore": quitting_player.score,
            "remainingPlayerScore": remaining_player.score,
            "message": f"Player {quitting_player.id} has quit the game."
        }

        # Emit the `quit_game` event to all connected clients in the game session
        for receiver_sid in game_instance.sids:
            if receiver_sid == sid:
                continue
            await sio.emit('quit_game', json_data, room=receiver_sid)

        # End the game and remove it from active games
        await game_instance.end_game()
        if game_id in active_games:
            del active_games[game_id]
        logging.info(f"Game {game_id} terminated after player {player_id} quit.")
    else:
        logging.error(f"Game ID {game_id} not found.")

# Event handler for test message
# This function is called when a client sends a test message to the server
@sio.event
async def test(sid):
    await sio.emit('test', {'message': 'Test message'}, room=sid)

def start_uvicorn():
    uvicorn.run(app, host='0.0.0.0', port=8010, log_level="info", log_config=logging_config)

async def check_timed_out_requests():
    for request in remote_game_requests[:]: #make a shallow coppy so it doesnt affect current for loop
        if await request.has_timed_out() is True:
            remote_game_requests.remove(request)


async def main():
    uvicorn_thread = threading.Thread(target=start_uvicorn, daemon=True)
    uvicorn_thread.start()
    # while 1:
    #      await check_timed_out_requests()
    uvicorn_thread.join()


if __name__ == '__main__':
    asyncio.run(main())
