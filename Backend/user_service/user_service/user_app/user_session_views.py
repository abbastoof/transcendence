import json
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserProfileModel as User
from .serializers import UserSerializer
from .models import UserProfileModel
from datetime import timedelta
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
import logging
import requests
import random
import os
from dotenv import load_dotenv

load_dotenv()
TOEKNSERVICE = os.environ.get('TOKEN_SERVICE')

headers = {
    "X-SERVICE-SECRET": settings.SECRET_KEY  # Replace with your actual secret key
}

logger = logging.getLogger(__name__)

def generate_password():
    return random.randint(100000,999999)
class UserLoginView(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def authenticate_user(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        status_code = status.HTTP_200_OK
        response = {}
        response_message = {}
        if username and password:
            user = authenticate(username=username, password=password)
        if user is not None:
            return True
        return False

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
                    # send post request to token-service
                    if user.otp_status:
                        user.otp = generate_password()
                        user.otp_expiry_time = now() + timedelta(minutes=1)
                        user.save()
                        send_mail(
                            'Verification Code',
                            f'Your verification code is: {user.otp}',
                            settings.EMAIL_HOST_USER,
                            [user.email],
                            fail_silently=False,
                        )
                        response_message = {"detail":"Verification password sent to your email"}
                        status_code = status.HTTP_200_OK
                    else:
                        data = {"id": serializer.data["id"], "username": serializer.data["username"]}
                        response = requests.post(f"{TOEKNSERVICE}/auth/token/gen-tokens/", data=data, headers=headers)
                        if response.status_code == 201:
                            response_message = response.json()
                        logger.info('user_data = %s', response.json())
                        if "error" in response_message:
                            status_code = response_message.get("status_code")
                            response_message = response.json()
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

    def verify_otp(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        otp = request.data.get("otp")
        response_message = {}
        status_code = status.HTTP_200_OK
        if username and password:
            user = authenticate(username=username, password=password)
        if user is not None:
            if user.otp_status:
                if user.otp == otp:
                    if user.otp_expiry_time > now():
                        data = {"id": user.id, "username": username}
                        response = requests.post(f'{TOEKNSERVICE}/auth/token/gen-tokens/', data=data)
                        user.otp = None
                        user.otp_expiry_time = None
                        if response.status_code == 201:
                            response_message = response.json()
                        logger.info('user_data = %s', response_message)
                        if "error" in response_message:
                            status_code = response_message.get("status_code")
                        else:
                            status_code = status.HTTP_200_OK
                    else:
                        response_message = {"error":"expired password"}
                        status_code = status.HTTP_401_UNAUTHORIZED
                else:
                    response_message = {"error":"Invalid password"}
                    status_code = status.HTTP_401_UNAUTHORIZED
            else:
                response_message = {"error":"You have not enable 2FA yet!"}
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
                response_message = {"detail": "Access token is required"}
                status_code =status.HTTP_400_BAD_REQUEST
            access_token = bearer.split(' ')[1]
            data = {"id":pk, "access": access_token}
            response_data = requests.post(f"{TOEKNSERVICE}/auth/token/invalidate-tokens/", data=data)
            if response_data.status_code == 200:
                response_message = response_data.json()
            if "error" in response_message:
                status_code = response_message.get("status_code")
            else:
                response_message = {"detail": "User logged out successfully"}
                status_code = status.HTTP_200_OK
        return Response(response_message, status=status_code)
