# from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from user_auth.views import CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
