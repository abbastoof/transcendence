# game_data/serializers.py

from rest_framework import serializers
from .models import GameHistory, GameStat

class GameHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GameHistory
        fields = '__all__'
class GameStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameStat
        fields = '__all__'
