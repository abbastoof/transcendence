from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfileModel
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=UserProfileModel)
def send_onlineStatus(sender, instance, created, **kwargs):
    if not created:
        channel_layer = get_channel_layer()
        user = instance.username
        user_status = instance.online_status

        data = {
            'username':user,
            'status':user_status
        }
        async_to_sync(channel_layer.group_send)(
            'online_status', {
                'type':'send_onlineStatus',
                'value':json.dumps(data)
            }
        )
