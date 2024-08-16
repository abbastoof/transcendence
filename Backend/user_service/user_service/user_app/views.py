import json
from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from .models import UserProfileModel, FriendRequest
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from .serializers import UserSerializer, FriendSerializer
from django.conf import settings
import requests
from dotenv import load_dotenv
import os

load_dotenv()
TOEKNSERVICE = os.environ.get('TOKEN_SERVICE')

headers = {
    "X-SERVICE-SECRET": settings.SECRET_KEY  # Replace with your actual secret key
}

def extract_token(request):
    bearer = request.headers.get("Authorization")
    if not bearer or not bearer.startswith('Bearer '):
        raise ValidationError(
            detail={"error": "Access token is required"},
            code=status.HTTP_400_BAD_REQUEST)
    access_token = bearer.split(' ')[1]
    return access_token

def validate_token(request) -> None:
    access_token = extract_token(request)
    if access_token:
        data = {"id": request.user.id, "access": access_token}
        response = requests.post(f"{TOEKNSERVICE}/auth/token/validate-token/", data=data, headers=headers)
        response_data = response.json()
        if "error" in response_data:
            raise ValidationError(detail=response_data, code=response_data.get("status_code"))

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
            validate_token(request)
            users = UserProfileModel.objects.all()
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
            data = get_object_or_404(UserProfileModel, id=pk)
            if request.user != data:
                return Response({"detail": "You're not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = UserSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    @parser_classes([MultiPartParser, FormParser])
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
            data = get_object_or_404(UserProfileModel, id=pk)
            if data != request.user and not request.user.is_superuser:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            serializer = UserSerializer(instance=data, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        except ValidationError as err:
            item_lists = []
            for item in err.detail:
                item_lists.append(item)
            return Response({'error': item_lists}, status=status.HTTP_400_BAD_REQUEST)
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
            data = get_object_or_404(UserProfileModel, id=pk)
            if data != request.user and not request.user.is_superuser:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            access_token = extract_token(request)
            request_data = {"id":pk, "access": access_token}
            response_data = requests.post(f"{TOEKNSERVICE}/auth/token/invalidate-tokens/", data=request_data, headers=headers)
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
            if serializer.errors:
                data = serializer.errors
                if "email" in data:
                    data["email"] = ["A user with that email already exists."]
            return Response({"error":data}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as err:
            item_lists = []
            for item in err.detail:
                item_lists.append(item)
            return Response({'error': item_lists}, status=status.HTTP_400_BAD_REQUEST)

class FriendsViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def friends_list(self, request, user_pk=None):
        try:
            validate_token(request)
            user = get_object_or_404(UserProfileModel, id=user_pk)
            serializer = UserSerializer(user.friends.all(), many=True)
            data = [{"id": item["id"], "username": item["username"], "status": item["online_status"]} for item in serializer.data]
            return Response(data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


    def remove_friend(self, request, user_pk=None, pk=None):
        try:
            validate_token(request)
            user = get_object_or_404(UserProfileModel, id=user_pk)
            friend = get_object_or_404(UserProfileModel, id=pk)
            if friend in user.friends.all():
                user.friends.remove(friend)
                return Response({"detail": "Friend removed"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"detail": "Friend not in user's friends list"}, status=status.HTTP_404_NOT_FOUND)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


    def send_friend_request(self, request, user_pk=None):
        response_message = {}
        status_code = 0
        try:
            validate_token(request)
            current_user = get_object_or_404(UserProfileModel, id=user_pk)
            current_user_friends = current_user.friends.all()
            friend_username = request.data.get("username")
            if not friend_username:
                response_message = {"error": "Username is required"}
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                receiver = get_object_or_404(UserProfileModel, username=friend_username)
                if (user_pk == receiver.id):
                    response_message = {"error":"You can't send a friend request to yourself"}
                    status_code =status.HTTP_400_BAD_REQUEST
                elif receiver in current_user_friends:
                    response_message = {"error":"You're already friends"}
                    status_code =status.HTTP_400_BAD_REQUEST
                else:
                    existing_request = FriendRequest.objects.filter(
                    (Q(sender_user=current_user) & Q(receiver_user=receiver) & Q(status='pending')) |
                    (Q(sender_user=receiver) & Q(receiver_user=current_user) & Q(status='pending'))
                    ).first()

                    if existing_request:
                        if existing_request.sender_user == current_user:
                            existing_request.delete()
                            response_message = {"detail": "You withdrew your request"}
                            status_code = status.HTTP_200_OK
                        else:
                            response_message = {"error": "You have a pending friend from this user."}
                            status_code = status.HTTP_400_BAD_REQUEST
                    else:
                        FriendRequest.objects.create(sender_user=current_user, receiver_user=receiver, status='pending')
                        response_message = {"detail": "Friend request sent"}
                        status_code = status.HTTP_201_CREATED
            return Response(response_message, status=status_code)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def accept_friend_request(self, request, user_pk=None, pk=None):
        try:
            validate_token(request)
            current_user = get_object_or_404(UserProfileModel, id=user_pk)
            sender_user = get_object_or_404(UserProfileModel, id=pk)
            pending_requests = FriendRequest.objects.filter(receiver_user=current_user, sender_user=sender_user, status='pending')
            if pending_requests.exists():
                for req in pending_requests:
                    current_user.friends.add(sender_user)
                    sender_user.friends.add(current_user)
                    req.delete()
                return Response({"detail": "Request accepted"}, status=status.HTTP_202_ACCEPTED)
            return Response({"detail": "No pending requests found"}, status=status.HTTP_404_NOT_FOUND)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


    def reject_friend_request(self, request, user_pk=None, pk=None):
        try:
            validate_token(request)
            current_user = get_object_or_404(UserProfileModel, id=user_pk)
            sender_user = get_object_or_404(UserProfileModel, id=pk)
            pending_request = FriendRequest.objects.filter(receiver_user=current_user, sender_user=sender_user, status='pending').first()
            if pending_request:
                pending_request.delete()
                return Response({"detail": "Request rejected"}, status=status.HTTP_202_ACCEPTED)
            return Response({"detail": "No pending requests found"}, status=status.HTTP_404_NOT_FOUND)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


    def friend_requests(self, request, user_pk=None): # get user pending list
        try:
            validate_token(request)
            user = get_object_or_404(UserProfileModel, id = user_pk)
            pending_requests = FriendRequest.objects.filter(receiver_user=user, status='pending') # filter returns a list
            data = FriendSerializer(pending_requests, many=True)
            return Response(data.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

