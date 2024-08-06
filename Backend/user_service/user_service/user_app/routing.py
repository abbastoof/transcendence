from django.urls import re_path
from . import NotificationConsumer, PersonalChatConsumer, OnlineStatusConsumer

websocket_urlpatterns = [
    re_path(r'ws/notify/', NotificationConsumer.NotificationConsumer.as_asgi()),
    re_path(r'ws/online/', OnlineStatusConsumer.OnlineStatusConsumer.as_asgi()),
    re_path(r'ws/<int:id>/', PersonalChatConsumer.PersonalChatConsumer.as_asgi()),
]
