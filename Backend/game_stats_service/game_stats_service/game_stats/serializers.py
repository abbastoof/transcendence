from rest_framework import serializers
from .models import GameStats

class GameStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameStats
        fields = '__all__'
