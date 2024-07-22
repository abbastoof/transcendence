from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
from django.utils.text import slugify
import uuid
import os

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('', instance.id, filename)

class User(AbstractUser):
    """
        User class to define the user model.

        This class inherits from AbstractUser. It defines the fields of the user model.

        Attributes:
            REQUIRED_FIELDS: The list of required fields for the user model.

        Email: The email field is required for the user model.
    """
    avatar = models.ImageField(upload_to=user_directory_path, null=True, blank=True, default='default.jpg')
    friends = models.ManyToManyField("self", blank=True, symmetrical=True)
    status = models.BooleanField(default=False)
    REQUIRED_FIELDS = ["email"]

class FriendRequest(models.Model):
    sender_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def accept(self):
        self.receiver_user.friends.add(self.sender_user)
        self.sender_user.friends.add(self.receiver_user)
        self.status = 'accepted'
        self.save()

    def reject(self):
        self.status='rejected'
        self.save()

    def __str__(self):
        return f"Friend request from {self.sender_user} to {self.receiver_user}"

    class Meta:
        unique_together = ('sender_user', 'receiver_user')
