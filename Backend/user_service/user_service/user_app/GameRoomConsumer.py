import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from channels.db import database_sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GAME_HISTORY_URL = settings.GAME_HISTORY_URL

@method_decorator(csrf_exempt, name='dispatch')
class GameRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from django.contrib.auth.models import AnonymousUser
        token = self.get_token_from_query_string()
        if token is None:
            await self.close(code=4001)
            return
        player = await self.get_user_from_token(token)
        if isinstance(player, AnonymousUser):
            await self.close(code=4001)
            return
        self.scope['user'] = player
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        room_obj = await self.set_room_and_player(player)
        self.room_group_name = self.room_name
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        if room_obj is None:
            await self.close(4001)
            return
        await self.send_notification("broadcast_message", 'entered room', self.scope['user'].username)
        asyncio.sleep(1)
        res = await self.check_room_players()
        if res:
            asyncio.sleep(1)
            response = await self.create_and_send_game_history_record()
            await self.send_notification('starting_game', response, self.scope['user'].username)

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

    @database_sync_to_async
    def set_room_and_player(self, player):
        from .models import GameRoom
        gameroom_obj, create = GameRoom.objects.get_or_create(room_name=self.room_name)
        if create:
            gameroom_obj.player1 = player
        else:
            if gameroom_obj.player1 is None:
                gameroom_obj.player1 = player
            elif (gameroom_obj.player1 is not None and gameroom_obj.player1 != player) and gameroom_obj.player2 is None:
                gameroom_obj.player2 = player
            else:
                return None
        gameroom_obj.save()
        return gameroom_obj

    async def disconnect(self, code):
        if hasattr(self, 'room_group_name') and self.room_group_name:
            self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            await self.remove_from_room()
            await self.send_notification("broadcast_message", 'left room', self.scope['user'].username)

    @database_sync_to_async
    def remove_from_room(self):
        from .models import GameRoom

        room_obj = GameRoom.objects.get(room_name = self.room_name)
        if room_obj is not None:
            if room_obj.player1 == self.scope['user']:
                room_obj.player1 = None
            elif room_obj.player2 == self.scope['user']:
                room_obj.player2 = None
            else:
                return
            room_obj.save()
            if room_obj.player1 is None and room_obj.player2 is None:
                room_obj.delete()
                return

    async def send_notification(self, type, message, user):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': type,
                'message': message,
                'player': user
            }
        )

    async def broadcast_message(self, event):
        message = event['message']
        player = event['player']
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message,
            'player': player
        }))

    async def starting_game(self, event):
        message = event['message']
        player = event['player']
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message,
            'player': player
        }))
    @database_sync_to_async
    def create_and_send_game_history_record(self):
        from .models import GameRoom
        from .serializers import GameRoomSerializer
        from django.utils.timezone import now

        request = {}
        response = {}
        gameroom_obj = GameRoom.objects.get(room_name=self.room_name)
        # Check if both players are present in the room and create a game history record if they are present
        if gameroom_obj is not None and gameroom_obj.player1 is not None and gameroom_obj.player2 is not None:
            serializer = GameRoomSerializer(gameroom_obj).data
            if serializer["player1_id"] and serializer["player2_id"]:
                request = {
                    "player1_id":serializer["player1_id"],
                    "player1_username":serializer["player1_username"],
                    "player2_id": serializer["player2_id"],
                    "player2_username": serializer["player2_username"],
                    "start_time": now()
                }
                response = requests.post(f'{GAME_HISTORY_URL}/game-history/', data=request)
        return response.json()

    @database_sync_to_async
    def check_room_players(self):
        from .models import GameRoom

        obj = GameRoom.objects.get(room_name = self.room_name)
        if obj is not None:
            if obj.player1 is not None and obj.player2 is not None:
                return True
        return False
