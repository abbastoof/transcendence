from django.db import models

class game_dataGameStats(models.Model):
    game_id = models.AutoField(primary_key=True)
    player1_score = models.IntegerField()
    player2_score = models.IntegerField()
    total_hits = models.IntegerField()
    longest_rally = models.IntegerField()

    def __str__(self):
        return f"Game {self.game_id}: {self.player1_score} vs {self.player2_score}"
