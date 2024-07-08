from django.urls import path
from .views import GameStatsViewSet

urlpatterns = [
    path(
        "game-stats/",
        GameStatsViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        ),
        name="gamestats-list",
    ),
    path(
        "game-stats/<int:pk>/",
        GameStatsViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="gamestats-detail",
    ),
]
