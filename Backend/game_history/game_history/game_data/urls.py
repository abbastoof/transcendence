from django.urls import path
from .views import GameHistoryViewSet

urlpatterns = [
    path(
        "game-history/",
        GameHistoryViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        ),
        name="game-history-list",
    ),
    path(
        "game-history/<int:pk>/",
        GameHistoryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="game-history-detail",
    ),
]
