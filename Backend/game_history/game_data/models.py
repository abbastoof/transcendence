# models.py
from django.db import models

class GameHistory(models.Model):
    game_id = models.AutoField(primary_key=True)
    player1_id = models.IntegerField()  # Reference to UserID in UserDB
    player2_id = models.IntegerField()  # Reference to UserID in UserDB
    winner_id = models.IntegerField()  # Reference to UserID in UserDB
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game {self.game_id}: {self.player1_id} vs {self.player2_id} - Winner: {self.winner_id}"
