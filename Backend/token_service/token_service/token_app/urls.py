# from django.contrib import admin
from django.urls import path
from .views import CustomTokenRefreshView, CustomTokenObtainPairView, InvalidateToken, ValidateToken

urlpatterns = [
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh",),
    path("auth/token/gen-tokens/", CustomTokenObtainPairView.as_view(), name="generate_tokens",),
    path("auth/token/invalidate-tokens/", InvalidateToken.as_view({"post": "invalidate_token_for_user",}), name="invalidate_tokens",),
    path("auth/token/validate-token/", ValidateToken.as_view({"post": "validate_token_for_user",}), name="validate_token",),
]
