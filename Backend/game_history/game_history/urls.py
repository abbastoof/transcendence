# game_history/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from game_data.views import GameHistoryViewSet

router = DefaultRouter()
router.register(r'game-history', GameHistoryViewSet, basename='gamehistory')

urlpatterns = [
    path('', include(router.urls)),
]
