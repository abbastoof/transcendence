import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import threading
from channels.db import database_sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class OnlineStatusConsumer(AsyncWebsocketConsumer):
    waiting_list = []
    user_channels = {}
    response_queues = {}

    async def connect(self):
        token = self.get_token_from_query_string()
        if token is None:
            await self.close(code=4001)
            return
        self.scope['user'] = await self.get_user_from_token(token)
        self.room_group_name = 'online_status'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.change_online_status(self.scope['user'], 'open')
        self.user_channels[self.scope['user'].username] = self.channel_name
        # print(f'Connected to WebSocket: {self.room_group_name}')
        await self.add_player_to_lobby(self.scope['user'])

    # Extract token from Query string
    def get_token_from_query_string(self):
        query_string = self.scope['query_string'].decode()
        if '=' in query_string:
            params = dict(param.split('=') for param in query_string.split('&'))
            return params.get('token')
        return None

    # Extract user from token
    @database_sync_to_async
    def get_user_from_token(self, token):
        from django.contrib.auth.models import AnonymousUser
        from .models import UserProfileModel
        from rest_framework_simplejwt.tokens import AccessToken, TokenError
        from rest_framework_simplejwt.exceptions import InvalidToken
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return UserProfileModel.objects.get(id=user_id)
        except (UserProfileModel.DoesNotExist, TokenError, InvalidToken):
            return AnonymousUser()

    # Add player to the lobby
    async def add_player_to_lobby(self, user):
        if user not in self.waiting_list:
            self.waiting_list.append(user)
            if len(self.waiting_list) > 1:
                player1 = self.waiting_list.pop(0)
                player2 = self.waiting_list.pop(0)
                await self.match_players(player1, player2)
                asyncio.create_task(self.wait_for_responses(player1, player2))
        else:
            pass

    # Match two players
    async def match_players(self, player1, player2):
        await self.channel_layer.send(
            self.user_channels[player1.username],
            {
                'type': 'match_found',
                'message': f'Match found with {player2.username}',
                'player': player2.username
            }
        )
        await self.channel_layer.send(
            self.user_channels[player2.username],
            {
                'type': 'match_found',
                'message': f'Match found with {player1.username}',
                'player': player1.username
            }
        )

    # Send match players notifications
    async def match_found(self, event):
        message = event['message']
        player = event['player']
        # Handle the match found event here
        await self.send(text_data=json.dumps({
            'message': message,
            'player': player
        }))

    async def wait_for_responses(self, player1, player2):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.await_response(player1)),
            loop.create_task(self.await_response(player2))
        ]
        done, pending = await asyncio.wait(tasks, timeout=5)

        if pending:
            for task in pending:
                task.cancel()
            await self.handle_match_timeout(player1)
            await self.handle_match_timeout(player2)
            logger.info(f"Match response timed out for {player1.username} and {player2.username}")

    # Wait for players response
    async def await_response(self, player):
        try:
            self.response_queues[player.username] = asyncio.Queue()
            response = await self.response_queues[player.username].get()
            logger.info(f"Received response from {player.username}: {response}")
            # Handle response here
        except asyncio.CancelledError:
            logger.info(f"Cancelled waiting for {player.username}'s response")

    # Receive messages from the users connected to the Websocket
    async def receive(self, text_data: str = "", bytes_data=None):
        # print(f'Received message: {text_data}')
        try:
            if text_data:
                data = json.loads(text_data)
                connection_type = data['type']
                if connection_type in ['match_accepted', 'match_rejected']:
                    if self.scope['user'].username in self.response_queues:
                        await self.response_queues[self.scope['user'].username].put(data)
                if "username" in data:
                    username = data['username']
                    # print(f'Parsed data: {data}')
                    if connection_type == 'close':
                        await self.close()
                    await self.change_online_status(username, connection_type)

        except json.JSONDecodeError as e:
            # print(f'JSON decode error: {e}')
            await self.close(code=4001)
        except KeyError as e:
            # print(f'Missing key: {e}')
            await self.close(code=4002)
        except Exception as e:
            # print(f'Error in receive: {e}')
            await self.close(code=1011)

    # Handle match accepted from users    
    async def handle_match_accepted(self, data):
        data_type = data["type"]
        player = self.scope["user"]
        target = data["player"]
        await self.channel_layer.send(
            self.user_channels[target],
            {
                'type': 'match_accepted',
                'message': f'{player.username} accepted the match',
            }
        )
    
    # match accepted function
    async def match_accepted(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
        }))

    # Handle match rejected from users  
    async def handle_match_rejected(self, data):
        data_type = data["type"]
        player = self.scope["user"]
        target = data["player"]
        await self.channel_layer.send(
            self.user_channels[target],
            {
                'type': 'match_rejected',
                'message': f'{player.username} rejected the match',
            }
        )

    async def match_rejected(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
        }))
    
    async def send_timeout_notification(self, player1, player2):
        await self.channel_layer.send(
            self.user_channels[player1.username],
            {
                'type': 'match_timeout',
                'message': f'Match response timed out',
            }
        )
        await self.channel_layer.send(
            self.user_channels[player2.username],
            {
                'type': 'match_timeout',
                'message': f'Match response timed out',
            }
        )

    async def match_timeout(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
        }))

    async def send_onlineStatus(self, event):
        try:
            data = json.loads(event.get('value'))
            username = data['username']
            online_status = data['status']
            print(f'Sending status: {data}')
            await self.send(text_data=json.dumps({
                'username': username,
                'online_status': online_status
            }))
        except json.JSONDecodeError as e:
            print(f'JSON decode error in send_onlineStatus: {e}')
        except KeyError as e:
            print(f'Missing key in send_onlineStatus: {e}')
        except Exception as e:
            print(f'Error in send_onlineStatus: {e}')


    @database_sync_to_async
    def change_online_status(self, username, c_type):
        from .models import UserProfileModel as User

        try:
            userprofile = User.objects.get(username=username)
            # print(f'User profile username: {userprofile.username}')
            if c_type == 'open':
                userprofile.online_status = True
                userprofile.save()
            else:
                userprofile.online_status = False
                userprofile.save()
            # print(f'Changed status for {username} to {c_type}')
        except User.DoesNotExist:
            print(f'User {username} does not exist.')
        except User.DoesNotExist:
            print(f'User profile for {username} does not exist.')
        except Exception as e:
            print(f'Error changing status: {e}')

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.change_online_status(self.scope['user'], 'close')
        # print(f'Disconnected from WebSocket: {self.room_group_name} with code: {code}')
        if self.scope['user'] in self.waiting_list:
            self.waiting_list.remove(self.scope['user'])