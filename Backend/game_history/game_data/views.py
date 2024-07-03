# game_data/views.py

from rest_framework import viewsets
from .models import GameHistory
from .serializers import GameHistorySerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
class GameHistoryViewSet(viewsets.ModelViewSet):
    queryset = GameHistory.objects.all()
    serializer_class = GameHistorySerializer

    def create_game_history(self, request):
        data = request.data
        serializer = GameHistorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def game_history_list(self, request):
        """
            Method to get the list of game history.

            This method gets the list of game history from the database and returns the list of game history.

            Args:
                request: The request object.

            Returns:
                Response: The response object containing the list of game history.
        """
        game_history = GameHistory.objects.all()
        serializer = GameHistorySerializer(game_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve_game_history(self, request, pk=None):
        """
            Method to retrieve a game history.

            This method retrieves a game history from the database using the game history id and returns the game history data.

            Args:
                request: The request object.
                pk: The primary key of the game history.

            Returns:
                Response: The response object containing the game history data.
        """
        data = get_object_or_404(GameHistory, id=pk)
        serializer = GameHistorySerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update_game_history(self, request, pk=None):
        """
            Method to update a game history.

            This method updates a game history in the database using the game history id and the data in the request.

            Args:
                request: The request object containing the game history data.
                pk: The primary key of the game history.

            Returns:
                Response: The response object containing the updated game history data.
        """
        data = get_object_or_404(GameHistory, id=pk)
        serializer = GameHistorySerializer(data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy_game_history(self, request, pk=None):
        """
            Method to delete a game history.

            This method deletes a game history from the database using the game history id.

            Args:
                request: The request object.
                pk: The primary key of the game history.

            Returns:
                Response: The response object containing the status of the deletion.
        """
        data = get_object_or_404(GameHistory, id=pk)
        data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
