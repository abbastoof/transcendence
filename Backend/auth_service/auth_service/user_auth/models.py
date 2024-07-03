from django.db import models

class UserTokens(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(unique=True)
    token_data = models.JSONField(null=True)

    def __str__(self):
        return self.username