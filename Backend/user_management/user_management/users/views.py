import json

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User
from .rabbitmq_utils import consume_message, publish_message
from .serializers import UserSerializer


class UserViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def users_list(self, request):
        if not request.user.is_staff or not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve_user(self, request, pk=None):
        data = get_object_or_404(User, id=pk)
        serializer = UserSerializer(data)
        return Response(serializer.data)

    def update_user(self, request, pk=None):
        data = get_object_or_404(User, id=pk)
        if data != request.user and not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(instance=data, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # if User updated Username should send message to all microservices to update the username related to this user using Kafka
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy_user(self, request, pk=None):
        data = get_object_or_404(User, id=pk)
        if data != request.user and not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        # Should send message to all microservices to delete all data related to this user using Kafka
        data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod  # This method is static because it doesn't need to access any instance variables
    @method_decorator(
        csrf_exempt
    )  # This decorator is used to disable CSRF protection for this method because it is called by RabbitMQ and not by a browser
    def handle_rabbitmq_request(ch, method, properties, body):
        payload = json.loads(body)
        username = payload.get("username")
        password = payload.get("password")

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Check if the user is active
            if user.is_active:
                serializer = UserSerializer(user)
                response_message = {"id": serializer.data["id"], "username": serializer.data["username"]}
            else:
                response_message = {"error": "User is inactive or staff"}
        else:
            response_message = {"error": "Invalid username or password"}
        print(f"Response message: {response_message}")
        publish_message("auth_response_queue", json.dumps(response_message))

    def start_consumer(self):
        consume_message("user_request_queue", self.handle_rabbitmq_request)


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create_user(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
