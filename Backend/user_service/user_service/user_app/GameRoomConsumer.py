import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from channels.db import database_sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)

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
        game_obj, create = GameRoom.objects.get_or_create(room_name=self.room_name)
        if create:
            game_obj.player1 = player
        else:
            if player != game_obj.player1:
                game_obj.player2 = player
        game_obj.save()
        #TODO:remove it
        from .serializers import GameRoomSerializer
        serializer = GameRoomSerializer(game_obj)
        logger.info("data = %s", serializer.data)
        return game_obj

    async def receive(self, text_data: str = "", bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            print(data)
            message = data['message']
            username = data['username']
            receiver = data['receiver']

            await self.save_message(username, self.room_group_name, message, receiver)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                }
            )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    async def disconnect(self, code):
        if hasattr(self, 'room_group_name') and self.room_group_name:
            self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    @database_sync_to_async
    def save_message(self, username, thread_name, message, receiver):
        from .models import ChatModel, ChatNotification, UserProfileModel

        chat_obj = ChatModel.objects.create(
            sender=username, message=message, thread_name=thread_name)
        other_user_id = self.scope['url_route']['kwargs']['id']
        get_user = UserProfileModel.objects.get(id=other_user_id)
        if receiver == get_user.username:
            ChatNotification.objects.create(chat=chat_obj, user=get_user)
