from rest_framework import viewsets, status
from .models import GameHistory, GameStat
from .serializers import GameHistorySerializer, GameStatSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .rabbitmq_utils import publish_message, consume_message
from django.utils.timezone import now
import json
import logging
from channels.db import database_sync_to_async
from aio_pika.message import IncomingMessage

logger = logging.getLogger(__name__)

    
@database_sync_to_async
def create_game_history_record(data):
    player1_id=data.get('player1_id')
    player2_id=data.get('player2_id')
    player1_username=data.get('player1_username')
    player2_username=data.get('player2_username')
    obj = GameHistory.objects.create(
        player1_id=player1_id,
        player1_username=player1_username,
        player2_id=player2_id,
        player2_username=player2_username,
        start_time=now()
    )
    serializer = GameHistorySerializer(obj)
    return serializer

async def handle_create_record_request(message: IncomingMessage):
    try:
        data = json.loads(message)
        serializer = await create_game_history_record(data)
        if serializer is not None:
            await publish_message("create_gamehistory_record_response", json.dumps(serializer.data))
    except Exception as err:
        logger.info('error = %s', err)
        error_message = {"error": str(err)}
        await publish_message("create_gamehistory_record_response", json.dumps(error_message))

async def start_consumer() -> None:
    await consume_message("create_gamehistory_record_queue", handle_create_record_request)

class GameHistoryViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing game history instances.
    """
    serializer_class = GameHistorySerializer
    queryset = GameHistory.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Create a new game history record.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """
        List all game history records.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) # serializer.data is a list of dictionaries containing the serialized data

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Retrieve a specific game history record.
        """
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Update a specific game history record.
        """
        partial = kwargs.pop('partial', False) # this line will remove the 'partial' key from the kwargs dictionary and return its value (False by default), because the partial argument is not needed in the update method
        instance = get_object_or_404(self.get_queryset(), pk=pk) # get the instance of the game history record
        serializer = self.get_serializer(instance, data=request.data, partial=partial) # create a serializer instance with the instance and the request data as arguments
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        Delete a specific game history record.
        """
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class GameStatViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing game stat instances.
    """
    serializer_class = GameStatSerializer
    queryset = GameStat.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Create a new game stat record.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """
        List all game stat records.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Retrieve a specific game stat record.
        """
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Update a specific game stat record.
        """
        partial = kwargs.pop('partial', False)
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        Delete a specific game stat record.
        """
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)