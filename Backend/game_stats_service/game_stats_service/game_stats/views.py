from rest_framework import viewsets, status
from .models import game_dataGameStats
from .serializers import GameStatsSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.request import Request

class GameStatsViewSet(viewsets.ModelViewSet):
    queryset = game_dataGameStats.objects.all()
    serializer_class = GameStatsSerializer

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, pk=None, *args: tuple, **kwargs: dict) -> Response:
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request: Request, pk=None, *args: tuple, **kwargs: dict) -> Response:
        partial = kwargs.pop('partial', False)
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: Request, pk=None, *args: tuple, **kwargs: dict) -> Response:
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
