# game_data/serializers.py

from rest_framework import serializers
from .models import GameHistory

class GameHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GameHistory
        fields = '__all__'
