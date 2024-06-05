from django.contrib import admin
from django.urls import path
from user.views import UserListView, UserDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
