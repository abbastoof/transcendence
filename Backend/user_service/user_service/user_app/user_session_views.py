import json
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserProfileModel as User
from .serializers import UserSerializer
from asgiref.sync import async_to_sync
import logging
import asyncio
import requests

logger = logging.getLogger(__name__)

class UserLoginView(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        status_code = status.HTTP_200_OK
        response = {}
        response_message = {}
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    serializer = UserSerializer(user)
                    data = {"id": serializer.data["id"], "username": serializer.data["username"]}
                    # send post request to token-service
                    response = requests.post("http://token-service:8000/auth/token/gen-tokens/", data=data)
                    if response.status_code == 201:
                        response_message = response.json()
                    logger.info('user_data = %s', response_message)
                    if "error" in response_message:
                        status_code = response_message.get("status_code")
                    else:
                        status_code = status.HTTP_200_OK
                else:
                    response_message = {"detail": "User is Inactive"}
                    status_code = status.HTTP_401_UNAUTHORIZED
            else:
                response_message = {"detail": "Invalid username or password"}
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            response_message = {"detail": "Username or password is missing"}
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(response_message, status=status_code)

class UserLogoutView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def logout(self, request, pk=None):
        response_message={}
        status_code = 0
        user = get_object_or_404(User, id=pk)
        if user != request.user:
            response_message = {"detail": "You're not authorized"}
            status_code=status.HTTP_401_UNAUTHORIZED
        else:
            bearer = request.headers.get("Authorization")
            if not bearer or not bearer.startswith('Bearer '):
                return Response({"detail": "Access token is required"}, code=status.HTTP_400_BAD_REQUEST)
            access_token = bearer.split(' ')[1]
            data = {"id":pk, "access": access_token}
            response_data = requests.post("http://token-service:8000/auth/token/invalidate-tokens/", data=data)
            if response_data.status_code == 200:
                response_message = response_data.json()
            if "error" in response_message:
                status_code = response_message.get("status_code")
            else:
                response_message = {"detail": "User logged out successfully"}
                status_code = status.HTTP_200_OK
        return Response(response_message, status=status_code)
