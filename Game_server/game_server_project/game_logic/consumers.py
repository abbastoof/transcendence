from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
from game_logic.game_defaults import *
from game_logic.entities.position import Position
from game_logic.entities.gamestate import GameState
from game_logic.entities.player import Player
from game_logic.entities.ball import Ball
from game_logic.entities.gamestate import GameState
import logging
import asyncio

game_loop_task = None

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "group"
        self.game_id = 1
        self.player1_id = 1
        self.player2_id = 2

        # #Join the game group
        await self.channel_layer.group_add(
             self.group_name,
             self.channel_name
        )

        await self.accept()

        # Send the default settings to the client
        await self.send(text_data=json.dumps({
            'PLAYER1_START_X': PLAYER1_START_X,
            'PLAYER2_START_X': PLAYER2_START_X,
            'BALL_DEFAULT_X': BALL_DEFAULT_X,
            'BALL_DEFAULT_Z': BALL_DEFAULT_Z,
            'BALL_RADIUS': BALL_RADIUS,
            'BALL_SPEED': BALL_SPEED,
            'BALL_DEFAULT_DIRECTION': BALL_DEFAULT_DIRECTION,
            # ... add other settings as needed ...
        }))

        global game_loop_task
        if game_loop_task is None:
            game_loop_task = asyncio.create_task(self.run_game())
            logging.info("Started game loop task")
            

    async def disconnect(self, close_code):
        # Leave the game group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        if not hasattr(self, 'game_state'):
            logging.error("Game state is not initialized")
            return
        data = json.loads(text_data)
        event_type = data['type']
        
        if event_type == 'move_paddle':
            player1_id = data['player1_id']
            p1_delta_z = data['p1_delta_z']
            player2_id = data['player2_id']
            p2_delta_z = data['p2_delta_z']
            self.game_state.move_player(player1_id, p1_delta_z)
            self.game_state.move_player(player2_id, p2_delta_z)
    
    async def run_game(self):
        self.game_state = self.init_game()
        while self.game_state.in_progress:
            self.game_state.current_rally = 0
            self.game_state.reset_ball()
            logging.info("Rally started")
            await self.send_initial_game_state()
            await asyncio.sleep(0.5)
            self.game_state.paused = False
            while not self.game_state.paused:
                await self.update_game_state()
                await asyncio.sleep(0.006)  # Add sleep to avoid tight loop
            await self.post_rally_animation()
            if self.game_state.current_rally > self.game_state.longest_rally:
                self.game_state.longest_rally = self.game_state.current_rally
    
    async def send_initial_game_state(self):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_game_state',
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
            }
        )

    async def post_rally_animation(self):
        for _ in range(40):  # Adjust the range to control the duration of the animation
            self.game_state.ball.update_position()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'send_game_state',
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
                }
            )
            await asyncio.sleep(0.006)  # Adjust this to control the speed of the animation

    async def update_game_state(self):
        self.game_state.ball.update_position()
        self.game_state.handle_collisions()
        if self.game_state.check_goal() == True:
            self.game_state.paused = True
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_game_state',
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
            }
        )

    def init_game(self) -> GameState:
        # Create the players
        player1 = Player(self.player1_id, PLAYER1_START_X)
        player2 = Player(self.player2_id, PLAYER2_START_X)
        
        # Create the ball
        ball = Ball(BALL_DEFAULT_X, BALL_DEFAULT_Z, BALL_RADIUS, BALL_SPEED, BALL_DEFAULT_DIRECTION)
        # Create the game state
        game_state = GameState(self.game_id, player1, player2, ball)
    
        return game_state


    async def send_game_state(self, event):
        await self.send(text_data=json.dumps({
            'type': 'send_game_state',
            'ball': event['ball'],
            'player1_position': event['player1_position'],
            'player2_position': event['player2_position'],
        }))
        
    # Receive message from game group
    async def game_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
