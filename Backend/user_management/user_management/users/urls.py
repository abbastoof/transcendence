from django.urls import path
from .views import RegisterViewSet, UserViewSet

urlpatterns = [
    path('user/register/', RegisterViewSet.as_view({
        'post': 'create_user',
    }), name='register-user'),
    path('user', UserViewSet.as_view({
        'get': 'users_list',
    }), name='users-list'),
    path('user/<int:pk>/', UserViewSet.as_view({
        'get': 'retrieve_user',
        'put': 'update_user',
        'delete': 'destroy_user',
    }), name='user-detail'),
]
