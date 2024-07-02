# from django.contrib import admin
from django.urls import path
from user_auth.views import CustomTokenObtainPairView, CustomTokenRefreshView, CustomLogoutView

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
]
