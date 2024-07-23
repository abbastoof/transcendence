import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')

django_asgi_app = get_asgi_application()

from user_app.consumers import NotificationConsumer, OnlineStatusConsumer, PersonalChatConsumer
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/<int:id>/", PersonalChatConsumer.as_asgi()),
                    path("ws/notify/", NotificationConsumer.as_asgi()),
                    path("ws/online/", OnlineStatusConsumer.as_asgi()),
                ]
            )
        )
    ),
})
