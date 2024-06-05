from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=200)
	username = models.CharField(max_length=200, unique=True)
	email = models.EmailField(max_length=200, unique=True, primary_key=True)
	password = models.CharField(max_length=200)

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = []