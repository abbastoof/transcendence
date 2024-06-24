from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    REQUIRED_FIELDS = ["email"]
