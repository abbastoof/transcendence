from channels.generic.websocket import AsyncWebsocketConsumer
import json
from game_logic.game_defaults import *
from .game_logic import run_game

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.game_id = self.scope['url_route']['kwargs']['game_id']
        # self.group_name = f'game_{self.game_id}'

        # # Join the game group
        # await self.channel_layer.group_add(
        #     self.group_name,
        #     self.channel_name
        # )

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
            

    async def disconnect(self, close_code):
        # Leave the game group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        player1_id = text_data_json['player1_id']
        player2_id = text_data_json['player2_id']

        # Run the game
        run_game(self.game_id, player1_id, player2_id)

        # Send message to game group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'game_message',
                'message': 'Game over'
            }
        )

    # Receive message from game group
    async def game_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from .game_logic import run_game

# class Consumers(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope["user"]
#         if self.user.is_authenticated:
#             await self.accept()
#         else:
#             await self.close()
    
#     async def disconnect(self, close_code):
#         pass

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
        
#         # Process keypress event
#         if text_data_json.get('type') == 'keypress':
#             key = text_data_json['key']
#             code = text_data_json['code']
#             key_code = text_data_json['keyCode']
#             alt_key = text_data_json['altKey']
#             ctrl_key = text_data_json['ctrlKey']
#             shift_key = text_data_json['shiftKey']

#             # Do something with the key press data
#             print(f"Key pressed: {key}, Code: {code}, KeyCode: {key_code}, Alt: {alt_key}, Ctrl: {ctrl_key}, Shift: {shift_key}")

#             # Send a response back to the client
#             await self.send(text_data=json.dumps({
#                 'message': f"Key {key} pressed"
#             }))