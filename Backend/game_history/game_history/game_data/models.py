# models.py
from django.db import models

class GameHistory(models.Model):
    game_id = models.AutoField(primary_key=True)
    player1_username = models.CharField(max_length=50)
    player1_id = models.IntegerField()
    player2_username = models.CharField(max_length=50)
    player2_id = models.IntegerField()
    winner_id = models.IntegerField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"Game {self.game_id}: {self.player1_username} vs {self.player2_username} - Winner: {self.winner_id}"

    REQUIRED_FIELDS = ['player1_id', 'player2_id']

class GameStat(models.Model):
    game_id = models.OneToOneField(GameHistory, on_delete=models.CASCADE, primary_key=True) # this field is a foreign key to the GameHistory model
    player1_score = models.IntegerField()
    player1_hits = models.IntegerField()
    player2_score = models.IntegerField()
    player2_hits = models.IntegerField()
    longest_rally = models.IntegerField()

    def __str__(self):
        return (f"Stats for Game {self.game_id.game_id}: {self.player1_score} vs {self.player2_score} - Longest Rally: {self.longest_rally}")
