from rest_framework import serializers
from .models import game_dataGameStats

class GameStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = game_dataGameStats
        fields = '__all__'
