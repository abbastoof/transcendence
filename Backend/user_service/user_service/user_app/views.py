from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import check_password, make_password
from .models import UserProfileModel, FriendRequest, ConfirmEmail
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from django.utils.timezone import now, timedelta
from .serializers import UserSerializer, FriendSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .user_session_views import generate_secret
import logging
import requests
from django.conf import settings

TOEKNSERVICE = settings.TOKEN_SERVICE_URL

logger = logging.getLogger(__name__)

headers = {
    "X-SERVICE-SECRET": settings.SECRET_KEY
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
            raise ValidationError(detail=response_data["error"], code=response_data.get("status_code"))

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

    @parser_classes([MultiPartParser, FormParser]) # we need to add this decorator to handle file uploads 
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
            response_message = {}
            status_code = status.HTTP_200_OK
            validate_token(request)
            user_obj = get_object_or_404(UserProfileModel, id=pk)
            if user_obj != request.user and not request.user.is_superuser:
                response_message = {"error": "You're not authorized"}
                status_code = status.HTTP_401_UNAUTHORIZED
            else:
                data = request.data
                current_email = user_obj.email
                if "email" in data:
                    response_message, status_code = self.handle_email(data, user_obj)
                if not response_message:
                    if "avatar" in data:
                        filename = data["avatar"]
                        logger.info(f"filename: {filename}")
                        ext = str(filename).split('.')[-1]
                        if ext and ext not in ['jpg', 'jpeg', 'png', 'bmp', 'gif']:
                            return Response({'error':'Unsupported file extension.'}, status= status.HTTP_400_BAD_REQUEST)
                        elif ext is None:
                            return Response({'error':'File extension required.'}, status= status.HTTP_400_BAD_REQUEST)
                        if user_obj.avatar != "default.jpg":
                            user_obj.avatar.delete(save=False)
                    serializer = UserSerializer(instance=user_obj, data=data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    if serializer.data["email"] != current_email.user_email:
                        current_email.delete()
                    response_message = serializer.data
                    status_code = status.HTTP_202_ACCEPTED
        except ValidationError as err:
            item_lists = []
            for item in err.detail:
                item_lists.append(item)
            response_message = {'error': item_lists}
            status_code = status.HTTP_400_BAD_REQUEST
        except Exception as err:
            response_message = {"error": str(err)}
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(response_message, status=status_code)

    def handle_email(self, data, user_obj):
        response_message = {}
        status_code = status.HTTP_200_OK
        new_email = data["email"]
        new_email_obj = ConfirmEmail.objects.filter(user_email=new_email).first()
        if new_email_obj and new_email_obj.verify_status:
            existing_user = UserProfileModel.objects.filter(email=new_email).exclude(id=user_obj.id).first()
            if existing_user:
                response_message = {"error": "Email already exists"}
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                data["email"] = new_email_obj.pk
        else:
            response_message = {"error": "You have not confirmed your email yet!"},
            status_code=status.HTTP_401_UNAUTHORIZED
        return response_message, status_code

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

    def send_email(self, email, otp):
        send_mail(
            'Email verification code',
            f'Your verification code is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

    def send_email_otp(self, request) -> Response:
        email = request.data.get("email")
        response_message = {}
        status_code = status.HTTP_200_OK
        if email is not None:
            try:
                email_obj, create = ConfirmEmail.objects.get_or_create(user_email=email)
                if email_obj.verify_status == False:
                    otp = generate_secret()
                    email_obj.otp = make_password(str(otp))
                    email_obj.otp_expiry_time = now() + timedelta(minutes=3)
                    email_obj.save()
                    self.send_email(email_obj.user_email, otp)
                    response_message = {"detail":"Email verification code sent to your email"}
                else:
                    response_message = {"error": "This email already verified."}
                    status_code = status.HTTP_401_UNAUTHORIZED
            except Exception as err:
                response_message = {"error": str(err)}
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            response_message = {"error": "email field required"}
            status_code = status.HTTP_404_NOT_FOUND
        return Response(response_message, status=status_code)

    def verify_email_otp(self, request) -> Response:
        response_message = {}
        status_code = status.HTTP_200_OK
        email = request.data.get('email')
        if email is not None:
            email_obj = get_object_or_404(ConfirmEmail, user_email = email)
            if email_obj.verify_status == False:
                otp = request.data.get('otp')
                if otp is not None:
                    if check_password(str(otp), email_obj.otp):
                        if email_obj.otp_expiry_time > now():
                            response_message = {"detail":"Email verified"}
                            email_obj.otp = None
                            email_obj.otp_expiry_time = None
                            email_obj.verify_status = True
                            email_obj.save()
                        else:
                            response_message = {"error":"otp expired"}
                            status_code = status.HTTP_401_UNAUTHORIZED
                    else:
                        response_message = {'error':"Invalid otp"}
                        status_code = status.HTTP_401_UNAUTHORIZED
                else:
                    response_message = {'error':'otp field required'}
                    status_code = status.HTTP_400_BAD_REQUEST
            else:
                response_message = {'error':'This email is already verified.'}
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            response_message = {'error': 'email field required'}
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(response_message, status=status_code)

    def available_username_email(self, request) -> Response:
        email = request.data.get("email")
        username = request.data.get("username")
        response_message = {}
        status_code = status.HTTP_200_OK
        if username is not None or email is not None:
            user_obj = UserProfileModel.objects.filter(username = username).first()
            email_obj = UserProfileModel.objects.filter(email = email).first()
            if user_obj is not None and email_obj is not None:
                response_message = {"error": "username and email are not available"}
                status_code = status.HTTP_400_BAD_REQUEST
            elif user_obj is not None:
                response_message = {"error": "username is not available"}
                status_code = status.HTTP_400_BAD_REQUEST
            elif email_obj is not None:
                response_message = {"error": "email is not available"}
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                if email is not None and username is not None:
                    response_message = {"detail": "username and email are available"}
                elif username is not None:
                    response_message = {"detail": "username is available"}
                elif email is not None:
                    response_message = {"detail": "email is available"}
        else:
            response_message = {'error':"username and email fields are required"}
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(response_message, status=status_code)

    def create_user(self, request) -> Response:
        """
            Method to create a new user.

            This method creates a new user by validating the data in the request and saving the user data to the database.

            Args:
                request: The request object containing the user data.
            Returns:
                Response: The response object containing the user data.
        """
        response_message = {}
        status_code = status.HTTP_201_CREATED
        try:
            email = request.data.get("email")
            email_obj = get_object_or_404(ConfirmEmail, user_email = email)
            result = UserProfileModel.objects.filter(email = email_obj.pk).first()
            if email_obj is not None:
                if email_obj.verify_status == True:
                    if result is not None:
                        response_message = {'error': {"email":"A user with that email already exists."}}
                        status_code=status.HTTP_400_BAD_REQUEST
                    else:
                        data = request.data
                        data["email"] = email_obj.pk
                        serializer = UserSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            response_message = serializer.data
                        if serializer.errors:
                            response_message = {"error":serializer.errors},
                            status_code=status.HTTP_400_BAD_REQUEST
                else:
                    response_message = {"error": "You have not confirmed your email yet!"},
                    status_code=status.HTTP_401_UNAUTHORIZED
        except Http404:
            response_message = {"error": "You have not verified your email yet!"}
            status_code = status.HTTP_401_UNAUTHORIZED
        except ValidationError as err:
            item_lists = []
            for item in err.detail:
                item_lists.append(item)
            response_message = {'error': item_lists}
            status_code=status.HTTP_400_BAD_REQUEST
        except Exception as err:
            response_message = {'error':str(err)}
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(response_message, status = status_code)

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

