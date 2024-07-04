# from django.contrib import admin
from django.urls import path
from user_auth.views import CustomTokenRefreshView, CustomLogoutView

urlpatterns = [
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
