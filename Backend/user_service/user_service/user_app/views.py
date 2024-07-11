import json
import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .models import User, FriendRequest
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
        try:
            self.send_data_to_user_service(request)
            if not request.user.is_staff or not request.user.is_superuser:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


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
        try:
            self.send_data_to_user_service(request)
            data = get_object_or_404(User, id=pk)
            serializer = UserSerializer(data)
            return Response(serializer.data)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

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
        try:
            self.send_data_to_user_service(request)
            data = get_object_or_404(User, id=pk)
            # if data != request.user and not request.user.is_superuser:
            #     return Response(status=status.HTTP_401_UNAUTHORIZED)
            serializer = UserSerializer(instance=data, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # if User updated Username should send message to all microservices to update the username related to this user using Kafka
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

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
        try:
            self.send_data_to_user_service(request)
            data = get_object_or_404(User, id=pk)
            if data != request.user and not request.user.is_superuser:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            # Should send message to all microservices to delete all data related to this user using Kafka
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def send_data_to_user_service(self, request) -> None:
        bearer = request.headers.get("Authorization")
        if not bearer or not bearer.startswith('Bearer '):
            raise ValidationError(detail= "Access token is required", code=status.HTTP_400_BAD_REQUEST)
        access_token = bearer.split(' ')[1]
        publish_message("validate_token_request_queue", json.dumps({"access": access_token}))

        response_data = {}

        def handle_response(ch, method, properties, body):
            nonlocal response_data
            response_data.update(json.loads(body))
            ch.stop_consuming()

        consume_message("validate_token_response_queue", handle_response)

        if "error" in response_data:
            raise ValidationError(detail= "Invalid access token", code=status.HTTP_401_UNAUTHORIZED)


    @staticmethod  # This method is static because it doesn't need to access any instance variables
    @method_decorator(
        csrf_exempt
    )  # This decorator is used to disable CSRF protection for this method because it is called by RabbitMQ and not by a browser
    def handle_login_request(ch, method, properties, body) -> None:
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
                serializer = UserSerializer(user, data={"status": True}, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                response_message = {"id": serializer.data["id"], "username": serializer.data["username"]}
            else:
                response_message = {"error": "User is inactive or staff"}
        else:
            response_message = {"error": "Invalid username or password"}
        print(f"Response message: {response_message}")
        publish_message("login_response_queue", json.dumps(response_message))

    def start_consumer(self) -> None:
        consume_message("login_request_queue", self.handle_login_request)


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

class FriendsViewSet(viewsets.ViewSet):
    def friends_list(self, request, user_pk=None):
        user = get_object_or_404(User, id=user_pk)
        if user is not None:
            serializer = UserSerializer(user.friends.all(), many=True)
            data = []
            for item in serializer.data:
                data.append({"username": item["username"], "status": item["status"]})
            return Response(data, status=status.HTTP_200_OK)
        return Response({"detail": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

    def remove_friend(self, request, user_pk=None, pk=None):
        pass

    # def add_friend(self, request, user_pk=None, pk=None):
    #     try:
    #         user = get_object_or_404(User, id=user_pk)
    #         friend = get_object_or_404(User, id=pk)
    #         user.friends.add(friend)
    #         user.save()
    #         return Response({"detail": "Friend added"}, status=status.HTTP_202_ACCEPTED)
    #     except User.DoesNotExist:
    #         return Response({"detail": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)

    def send_friend_request(self, request, user_pk=None, pk=None):
        try:
            current_user = get_object_or_404(User, id=user_pk)
            receiver = get_object_or_404(User, id=pk)
            friend_request, created = FriendRequest.objects.get_or_create(
                receiver_user = current_user,
                sender_user = receiver,
                status = 'pending'
            )
            if created:
                friend_request.save()
                return Response({"detail": "Requested"}, status=status.HTTP_202_ACCEPTED)
            return Response({"detail": f"Your request status is {friend_request.status}"}, status=status.HTTP_202_ACCEPTED)
        except User.DoesNotExist:
            return Response({"detail": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)

    def accept_friend_request(self, request, user_pk=None, pk=None):
        try:
            current_user = get_object_or_404(User, id=user_pk)
            pending_user = get_object_or_404(FriendRequest, id=pk)
            if pending_user.receiver_user == current_user:
                if pending_user.status == 'pending':
                    pending_user.status = 'accepted'
                    pending_user.accept()
                    pending_user.save()
            return Response({"detail": "Request accepted"}, status=status.HTTP_202_ACCEPTED)
        except User.DoesNotExist:
            return Response({"detail": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)
