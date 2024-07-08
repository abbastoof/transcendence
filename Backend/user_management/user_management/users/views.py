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
    """
        UserViewSet class to handle user related operations.

        This class inherits from ViewSet. It defines the methods to handle user related operations like
        getting the list of users, retrieving a user, updating a user, and deleting a user.

        Attributes:
            authentication_classes: The list of authentication classes to use for the view.
            permission_classes: The list of permission classes to use for the view.

        Methods:
            users_list: Method to get the list of users.
            retrieve_user: Method to retrieve a user.
            update_user: Method to update a user.
            destroy_user: Method to delete a user.
            handle_rabbitmq_request: Method to handle the RabbitMQ request.
            start_consumer: Method to start the RabbitMQ consumer.

    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def users_list(self, request) -> Response:
        """
            Method to get the list of users.

            This method gets the list of users from the database and returns the list of users.

            Args:
                request: The request object.

            Returns:
                Response: The response object containing the list of users.
        """
        if not request.user.is_staff or not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve_user(self, request, pk=None) -> Response:
        """
            Method to retrieve a user.

            This method retrieves a user from the database using the user id and returns the user data.

            Args:
                request: The request object.
                pk: The primary key of the user.

            Returns:
                Response: The response object containing the user data.
        """
        data = get_object_or_404(User, id=pk)
        serializer = UserSerializer(data)
        return Response(serializer.data)

    def update_user(self, request, pk=None) -> Response:
        """
            Method to update a user.

            This method updates a user in the database using the user id and the data in the request.

            Args:
                request: The request object containing the user data.
                pk: The primary key of the user.

            Returns:
                Response: The response object containing the updated user data.
        """
        data = get_object_or_404(User, id=pk)
        if data != request.user and not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(instance=data, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # if User updated Username should send message to all microservices to update the username related to this user using Kafka
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy_user(self, request, pk=None) -> Response:
        """
            Method to delete a user.

            This method deletes a user from the database using the user id.

            Args:
                request: The request object.
                pk: The primary key of the user.

            Returns:
                Response: The response object containing the status of the deletion.
        """
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
    def handle_rabbitmq_request(ch, method, properties, body) -> None:
        """
            Method to handle the RabbitMQ request.

            This method handles the RabbitMQ request by authenticating the user and sending the response message.

            Args:
                ch: The channel object.
                method: The method object.
                properties: The properties object.
                body: The body of the message.

            Returns:
                None

        """
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

    def start_consumer(self) -> None:
        consume_message("user_request_queue", self.handle_rabbitmq_request)


class RegisterViewSet(viewsets.ViewSet):
    """
        RegisterViewSet class to handle user registration.

        This class inherits from ViewSet. It defines the method to handle user registration.

        Attributes:
            permission_classes: The list of permission classes to use for the view.

        Methods:
            create_user: Method to create a new user.
    """
    permission_classes = [AllowAny]

    def create_user(self, request) -> Response:
        """
            Method to create a new user.

            This method creates a new user by validating the data in the request and saving the user data to the database.

            Args:
                request: The request object containing the user data.
            Returns:
                Response: The response object containing the user data.
        """
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
