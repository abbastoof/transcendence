import json
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserProfileModel as User
from .rabbitmq_utils import consume_message, publish_message
from .serializers import UserSerializer
from asgiref.sync import async_to_sync
from aio_pika.message import AbstractIncomingMessage
import logging
import asyncio

logger = logging.getLogger(__name__)

async def publish_consumer(data):
    await publish_message("user_token_request_queue", json.dumps(data))

    user_data = {}

    async def handle_response(message):
        nonlocal user_data
        data = json.loads(message.body.decode())
        user_data.update(data)
        await message.ack()

    await consume_message("user_token_response_queue", handle_response)

    logger.info('\ndata = %s\n', user_data)
    # Wait for user_data to be populated
    logger.info(f"Final user_data: {user_data}")
    return user_data

class UserLoginView(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        status_code = 0
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    serializer = UserSerializer(user, data={"online_status": True}, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    data = {"id": serializer.data["id"], "username": serializer.data["username"]}
                    user_data = {}
                    user_data = async_to_sync(publish_consumer)(data)
                    if "error" in user_data:
                        response_message = {"error": "Couldn't generate tokens", "status":status.HTTP_401_UNAUTHORIZED}
                    else:
                        response_message = user_data
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
            print("access=",access_token)
            publish_message("logout_request_queue", json.dumps({"id":pk, "access": access_token}))
            response_data = {}
            def handle_response(ch, method, properties, body):
                nonlocal response_data
                response_data.update(json.loads(body))
                ch.stop_consuming()
            consume_message("logout_response_queue", handle_response)
            print("response data = ", response_data)
            if "error" in response_data:
                response_message = {"error": response_data}
                status_code = status.HTTP_401_UNAUTHORIZED
            else:
                serializer = UserSerializer(instance=user, data={'online_status':False}, partial=True)
                serializer.is_valid()
                serializer.save()
                response_message = {"detail": "User logged out successfully"}
                status_code = status.HTTP_200_OK
        return Response(response_message, status=status_code)
