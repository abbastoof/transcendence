import json
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserProfileModel as User
from .serializers import UserSerializer
from datetime import timedelta
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
import logging
import requests
import secrets
import os
from dotenv import load_dotenv

load_dotenv()
TOEKNSERVICE = os.environ.get('TOKEN_SERVICE')

headers = {
    "X-SERVICE-SECRET": settings.SECRET_KEY
}

logger = logging.getLogger(__name__)

def generate_secret():
    return secrets.randbelow(900000) + 100000

class UserLoginView(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def send_email(self, email, otp):
        send_mail(
            'Verification Code',
            f'Your verification code is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

    def authenticate_user(self, request, username, password):
        if username and password:
            user = authenticate(username=username, password=password)
        if user is not None:
            return user
        return None

    def login(self, request):
        status_code = status.HTTP_200_OK
        response = {}
        response_message = {}
        username = request.data.get("username")
        password = request.data.get("password")
        if username and password:
            user = self.authenticate_user(request, username, password)
            if user is not None:
                if user.is_active:
                    serializer = UserSerializer(user)
                    if user.otp_status:
                        # 2FA is enabled
                        otp = generate_secret()
                        user.otp = make_password(str(otp))
                        user.otp_expiry_time = now() + timedelta(minutes=3)
                        user.save()
                        self.send_email(serializer.data["email"], otp)
                        response_message = {"detail":"Verification password sent to your email"}
                        status_code = status.HTTP_200_OK
                    else:
                        # 2FA is disabled
                        data = {"id": serializer.data["id"], "username": serializer.data["username"]}
                        response = requests.post(f"{TOEKNSERVICE}/auth/token/gen-tokens/", data=data, headers=headers)
                        if response.status_code == 201:
                            user.online_status = True
                            user.save()
                            response_message = response.json()
                        if "error" in response_message:
                            status_code = response_message.get("status_code")
                            response_message = response.json()
                else:
                    response_message = {"error": "User is Inactive"}
                    status_code = status.HTTP_401_UNAUTHORIZED
            else:
                response_message = {"error": "Invalid username or password"}
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            response_message = {"error": "username and password fields are required"}
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(response_message, status=status_code)

    def verify_otp(self, request): # frontend will send username, password and otp to verify the otp and login the user if the otp is correct
        status_code = status.HTTP_200_OK
        response = {}
        response_message = {}
        username = request.data.get("username")
        password = request.data.get("password")
        otp = request.data.get("otp")
        if username and password and otp:
            user = self.authenticate_user(request, username, password)
            if user is not None: # if the user is authenticated
                if user.otp_status: # if the user has enabled 2FA
                    if check_password(str(otp), user.otp):
                        if user.otp_expiry_time > now():
                            data = {"id": user.id, "username": username}
                            response = requests.post(f'{TOEKNSERVICE}/auth/token/gen-tokens/', data=data, headers=headers)
                            if response.status_code == 201:
                                response_message = response.json()
                                user.otp = None
                                user.otp_expiry_time = None
                                user.online_status = True
                                user.save()

                            if "error" in response_message:
                                status_code = response_message.get("status_code")
                            else:
                                status_code = status.HTTP_200_OK
                        else:
                            response_message = {"error":"expired code"}
                            status_code = status.HTTP_401_UNAUTHORIZED
                    else:
                        response_message = {"error":"Invalid code"}
                        status_code = status.HTTP_401_UNAUTHORIZED
                else:
                    response_message = {"error":"You have not enable 2FA yet!"}
                    status_code = status.HTTP_400_BAD_REQUEST
            else:
                response_message = {"error": "Invalid username or password"}
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            response_message = {"error": "username, password and otp fields are required"}
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
            response_data = requests.post(f"{TOEKNSERVICE}/auth/token/invalidate-tokens/", data=data, headers=headers)
            if response_data.status_code == 200:
                response_message = response_data.json()
            if "error" in response_message:
                status_code = response_message.get("status_code")
            else:
                response_message = {"detail": "User logged out successfully"}
                user.online_status = False
                user.save()
                status_code = status.HTTP_200_OK
        return Response(response_message, status=status_code)
