# game_data/models.py

from django.db import models

class GameHistory(models.Model):
    GameID = models.AutoField(primary_key=True)
    player1ID = models.IntegerField(unique=True)
    player2ID = models.IntegerField(unique=True)
    winner = models.CharField(max_length=255)
    score = models.CharField(max_length=50)
    match_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'game_data'

    def __str__(self):
        return f"{self.player1} vs {self.player2} - Winner: {self.winner} - Score: {self.score}"
