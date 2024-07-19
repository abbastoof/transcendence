from django.urls import path
from .views import GameHistoryViewSet, GameStatViewSet

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
    path(
        "game-stat/",
        GameStatViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        ),
        name="gamestat-list",
    ),
    path(
        "game-stat/<int:pk>/",
        GameStatViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="gamestat-detail",
    ),
]
