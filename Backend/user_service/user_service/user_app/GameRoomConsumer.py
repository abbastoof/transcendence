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
        if room_obj is None:
            logger.info('Room obj is None')
            await self.close(4001)
            return
        await self.send_notification(self.scope['user'].username, 'entered room')
        response = await self.create_game_history_record()
        if response is not None:
            logger.info('Response = %s',response)

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
            elif gameroom_obj.player1 is not None and gameroom_obj.player2 is None:
                gameroom_obj.player2 = player
            else:
                return None
        gameroom_obj.save()
        #TODO:remove it
        from .serializers import GameRoomSerializer
        serializer = GameRoomSerializer(gameroom_obj)
        logger.info("data = %s", serializer.data)
        return gameroom_obj

    async def disconnect(self, code):
        if hasattr(self, 'room_group_name') and self.room_group_name:
            self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            await self.remove_from_room()
            await self.send_notification(self.scope['user'].username, 'left room')

    @database_sync_to_async
    def remove_from_room(self):
        from .serializers import GameRoomSerializer
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
                logger.info('Room got deleted')
                return
            serializer = GameRoomSerializer(room_obj)
            if serializer is not None:
                logger.info('Room = %s', serializer.data)

    async def send_notification(self, player, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_message',
                'message': f'{player} {message}',
                'player': player
            }
        )

    async def broadcast_message(self, event):
        message = event['message']
        player = event['player']
        await self.send(text_data=json.dumps({
            'message': message,
            'player': player
        }))

    @database_sync_to_async
    def create_game_history_record(self):
        from .models import GameRoom
        from .serializers import GameRoomSerializer
        from .rabbitmq_utils import publish_message, consume_message
    
        gameroom_obj = GameRoom.objects.get(room_name=self.room_name)
        if gameroom_obj is not None and gameroom_obj.player1 is not None and gameroom_obj.player2 is not None:
            serializer = GameRoomSerializer(gameroom_obj).data
            if serializer["player1_id"] and serializer["player2_id"]:
                request = {
                    "player1_id":serializer["player1_id"],
                    "player1_username":serializer["player1_username"],
                    "player2_id":serializer["player2_id"],
                    "player2_username":serializer["player2_username"],
                }
                publish_message('create_gamehistory_record_queue', json.dumps(request))
                response = {}

                def handle_response(ch, method, properties, body):
                    nonlocal response
                    response.update(json.loads(body))
                    ch.stop_consuming()

                consume_message('create_gamehistory_record_response', handle_response)

                if 'error' in response:
                    return f'Could not create game_history record: {response}'
            
            return response
        return None