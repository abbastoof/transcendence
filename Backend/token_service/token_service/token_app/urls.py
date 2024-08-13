# from django.contrib import admin
from django.urls import path
from token_app.views import CustomTokenRefreshView, CustomTokenObtainPairView, InvalidateToken, ValidateToken

urlpatterns = [
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh",),
    path("token/gen-tokens/", CustomTokenObtainPairView.as_view({"post": "create_token_for_user",}), name="generate_tokens",),
    path("token/invalidate-tokens/", InvalidateToken.as_view({"post": "invalidate_token_for_user",}), name="invalidate_tokens",),
    path("token/validate-token/", ValidateToken.as_view({"post": "validate_token_for_user",}), name="validate_token",),
]
