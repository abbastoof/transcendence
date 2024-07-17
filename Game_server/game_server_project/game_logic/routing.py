from django.urls import re_path
from game_logic import consumers

websocket_urlpatterns = [
    re_path(r'ws/$', consumers.Consumers.as_asgi()),
]
