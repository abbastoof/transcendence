from django.urls import re_path
from . import GameRoomConsumer, OnlineStatusConsumer

websocket_urlpatterns = [
    re_path(r'ws/online/', OnlineStatusConsumer.OnlineStatusConsumer.as_asgi()),
    re_path(r'ws/game/room/(?P<room_name>\w+)/$', GameRoomConsumer.GameRoomConsumer.as_asgi()),
    ]
