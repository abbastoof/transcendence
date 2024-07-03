from django.urls import path

from .views import GameHistoryViewSet

urlpatterns = [
    path(
        "game-history/",
        GameHistoryViewSet.as_view(
            {
                "get": "game_history_list",
            }
        ),
        name="game-history-list",
    ),
    path(
        "game-history/<int:pk>/",
        GameHistoryViewSet.as_view(
            {
                "get": "retrieve_game_history",
                "put": "update_game_history",
                "delete": "destroy_game_history",
            }
        ),
        name="game-history-detail",
    ),
]
