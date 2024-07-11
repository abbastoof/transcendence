from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.


class User(AbstractUser):
    """
        User class to define the user model.

        This class inherits from AbstractUser. It defines the fields of the user model.

        Attributes:
            REQUIRED_FIELDS: The list of required fields for the user model.

        Email: The email field is required for the user model.
    """
    friends = models.ManyToManyField("self", null=True, symmetrical=True)
    status = models.BooleanField(default=False)
    REQUIRED_FIELDS = ["email"]
