import json
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from .models import User, FriendRequest
from .rabbitmq_utils import publish_message, consume_message
from .serializers import UserSerializer, FriendSerializer
from django.db.models import Q


def validate_token(request) -> None:
    bearer = request.headers.get("Authorization")
    if not bearer or not bearer.startswith('Bearer '):
        raise ValidationError(
            detail={"error": "Access token is required"},
            code=status.HTTP_400_BAD_REQUEST)
    access_token = bearer.split(' ')[1]
    publish_message("validate_token_request_queue", json.dumps({"id": request.user.id, "access": access_token}))

    response_data = {}

    def handle_response(ch, method, properties, body):
        nonlocal response_data
        response_data.update(json.loads(body))
        ch.stop_consuming()

    consume_message("validate_token_response_queue", handle_response)

    if "error" in response_data:
        raise ValidationError(detail={"error": "Invalid access token"},
            code=status.HTTP_401_UNAUTHORIZED
        )


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
    parser_classes = (MultiPartParser, FormParser)

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
            validate_token(request)
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
            validate_token(request)
            data = get_object_or_404(User, id=pk)
            if request.user != data:
                return Response({"detail": "You're not authorized"}, status=status.HTTP)
            serializer = UserSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
            validate_token(request)
            data = get_object_or_404(User, id=pk)
            if data != request.user and not request.user.is_superuser:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
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
            validate_token(request)
            data = get_object_or_404(User, id=pk)
            if data != request.user and not request.user.is_superuser:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            # Should send message to all microservices to delete all data related to this user using Kafka
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

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
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as err:
            return Response({'error': err}, status=status.HTTP_400_BAD_REQUEST)

class FriendsViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def friends_list(self, request, user_pk=None):
        try:
            
            validate_token(request)
            user = get_object_or_404(User, id=user_pk)
            serializer = UserSerializer(user.friends.all(), many=True)
            data = [{"username": item["username"], "status": item["status"]} for item in serializer.data]
            return Response(data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


    def remove_friend(self, request, user_pk=None, pk=None):
        try:
            validate_token(request)
            user = get_object_or_404(User, id=user_pk)
            friend = get_object_or_404(User, id=pk)
            if friend in user.friends.all():
                user.friends.remove(friend)
                user.save()
                return Response({"detail": "Friend removed"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"detail": "Friend not in user's friends list"}, status=status.HTTP_404_NOT_FOUND)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


    def send_friend_request(self, request, user_pk=None, pk=None):
        try:
            validate_token(request)
            if (user_pk == pk):
                raise ValidationError(detail={"You can't send a friend request to yourself"}, code=status.HTTP_400_BAD_REQUEST)

            current_user = get_object_or_404(User, id=user_pk)
            receiver = get_object_or_404(User, id=pk)

            existing_request = FriendRequest.objects.filter(
            (Q(sender_user=current_user) & Q(receiver_user=receiver) & Q(status='pending')) |
            (Q(sender_user=receiver) & Q(receiver_user=current_user) & Q(status='pending'))
            ).first()

            if existing_request:
                if existing_request.sender_user == current_user:
                    existing_request.delete()
                    return Response({"detail": "You withdrew your request"}, status=status.HTTP_200_OK)
                return Response({"detail": "You have a pending friend from this user."}, status=status.HTTP_400_BAD_REQUEST)

            FriendRequest.objects.create(sender_user=current_user, receiver_user=receiver, status='pending')
            return Response({"detail": "Friend request sent"}, status=status.HTTP_201_CREATED)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


    def accept_friend_request(self, request, user_pk=None, pk=None):
        try:
            validate_token(request)
            current_user = get_object_or_404(User, id=user_pk)
            sender_user = get_object_or_404(User, id=pk)
            pending_requests = FriendRequest.objects.filter(receiver_user=current_user, sender_user=sender_user, status='pending')
            if pending_requests.exists():
                for req in pending_requests:
                    req.accept()
                return Response({"detail": "Request accepted"}, status=status.HTTP_202_ACCEPTED)
            return Response({"detail": "No pending requests found"}, status=status.HTTP_404_NOT_FOUND)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


    def reject_friend_request(self, request, user_pk=None, pk=None):
        try:
            validate_token(request)
            current_user = get_object_or_404(User, id=user_pk)
            sender_user = get_object_or_404(User, id=pk)
            pending_request = FriendRequest.objects.filter(receiver_user=current_user, sender_user=sender_user, status='pending').first()
            if pending_request:
                pending_request.reject()
                return Response({"detail": "Request rejected"}, status=status.HTTP_202_ACCEPTED)
            return Response({"detail": "No pending requests found"}, status=status.HTTP_404_NOT_FOUND)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        
    def friend_requests(self, request, user_pk=None): # get user pending list
        try:
            validate_token(request)
            user = get_object_or_404(User, id = user_pk)
            pending_requests = FriendRequest.objects.filter(receiver_user=user, status='pending') # filter returns a list
            data = FriendSerializer(pending_requests, many=True)
            return Response(data.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)
