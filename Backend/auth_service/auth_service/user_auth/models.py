from django.db import models


# Create your models here.
class UserTokens(models.Model):
    username = models.CharField(unique=True)
    token_data = models.JSONField()

    def __str__(self):
        return self.username
