from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
# Create your models here.
from django.utils.text import slugify
import uuid
import os

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join(str(instance.id), filename)

class ConfirmEmail(models.Model):
    user_email = models.EmailField(unique=True, primary_key=True)
    verify_status = models.BooleanField(default=False)
    otp = models.CharField(null=True, blank=True)
    otp_expiry_time = models.DateTimeField(blank=True, null=True)

class UserProfileModel(AbstractUser):
    """
        User class to define the user model.

        This class inherits from AbstractUser. It defines the fields of the user model.

        Attributes:
            REQUIRED_FIELDS: The list of required fields for the user model.

        Email: The email field is required for the user model.
    """
    email = models.OneToOneField(ConfirmEmail, related_name='user_profile_email', on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_directory_path, null=True, blank=True, default='default.jpg')
    friends = models.ManyToManyField("self", blank=True, symmetrical=True)
    online_status = models.BooleanField(default=False)
    otp_status = models.BooleanField(default=False, blank=True, null=True)
    otp = models.CharField(blank=True, null=True)
    otp_expiry_time = models.DateTimeField(blank=True, null=True)
    REQUIRED_FIELDS = ["email"]

class FriendRequest(models.Model):
    sender_user = models.ForeignKey(UserProfileModel, related_name='sent_requests', on_delete=models.CASCADE)
    receiver_user = models.ForeignKey(UserProfileModel, related_name='received_requests', on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Friend request from {self.sender_user} to {self.receiver_user}"

    class Meta:
        unique_together = ('sender_user', 'receiver_user')

class GameRoom(models.Model):
    room_name = models.CharField(max_length=50, unique=True)
    player1 = models.ForeignKey(UserProfileModel, on_delete=models.CASCADE, null=True, related_name='player1')
    player2 = models.ForeignKey(UserProfileModel, on_delete=models.CASCADE, null=True, related_name='player2')
