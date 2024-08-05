# game_data/serializers.py

from rest_framework import serializers
from .models import GameHistory, GameStat

class GameHistorySerializer(serializers.ModelSerializer):
    game_summary = serializers.SerializerMethodField()
    class Meta:
        model = GameHistory
        fields = '__all__'
    def get_game_summary(self, obj):
        return str(obj)
class GameStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameStat
        fields = '__all__'
