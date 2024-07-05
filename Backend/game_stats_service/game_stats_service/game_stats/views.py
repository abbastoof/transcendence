from rest_framework import viewsets
from .models import GameStats
from .serializers import GameStatsSerializer

class GameStatsViewSet(viewsets.ModelViewSet):
    queryset = GameStats.objects.all()
    serializer_class = GameStatsSerializer
