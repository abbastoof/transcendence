import json
import logging
from django.http import Http404
from rest_framework import status
from token_service import settings
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import viewsets
from .serializers import CustomTokenObtainPairSerializer
from .models import UserTokens
import jwt
from rest_framework.permissions import AllowAny
from django.conf import settings

SECRET = settings.SECRET_KEY
from django.conf import settings

SECRET = settings.SECRET_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_secret(request, response_message, status_code):
    secret_key = request.headers.get('X-SERVICE-SECRET')
    if secret_key is None or secret_key != SECRET:
        response_message = {"error": "Unauthorized request"}
        status_code = status.HTTP_401_UNAUTHORIZED
    return response_message, status_code

class CustomTokenObtainPairView(TokenObtainPairView):
    """
        CustomTokenObtainPairView class to handle token request.

        This class inherits from TokenObtainPairView. It defines the method to handle the token request.

        Methods:
            handle_token_request: Method to handle the token request.
            start_consumer: Method to start the RabbitMQ consumer.
    """
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer # this is the serializer class that is used to generate the token for the user
    def post(self, request, *args, **kwargs) -> Response: # login endpoint will send the user id and username to generate a refresh token and access token for the user
        """
            Create a new token for the user.

            This method creates a new token for the user and returns the token details.

            Args:
                request: The request object.

            Returns:
                Response: The response object containing the token details.
        """

        response_message = {}
        status_code = status.HTTP_201_CREATED
        response_message, status_code = check_secret(request, response_message, status_code)
        if "error" not in response_message and status_code == status.HTTP_201_CREATED:
            id = request.data.get("id")
            username = request.data.get("username")
            if not username or not id:
                response_message = {"error": "Username and id are required"}
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                try:
                    user, create = UserTokens.objects.get_or_create(id=id, username=username)
                    if create:
                        refresh = RefreshToken.for_user(user)
                        access_token = str(refresh.access_token)
                        user.token_data = {
                            "refresh": str(refresh),
                            "access": access_token
                        }
                        user.save()
                        response_message = {
                            "id": id,
                            "refresh": str(refresh),
                            "access": access_token
                        }
                    else:
                        token_data = user.token_data
                        try:
                            refresh = RefreshToken.for_user(user)
                            token_data["refresh"] = str(refresh)
                            token_data["access"] = str(refresh.access_token)
                            user.token_data = token_data
                            user.save()
                            response_message = {
                                "id": id,
                                "refresh": str(refresh),
                                "access": token_data["access"]
                            }

                        except Exception as err:
                            response_message = {"error": str(err)}
                            status_code = status.HTTP_400_BAD_REQUEST
                except Exception as err:
                    response_message = {"error": str(err)}
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response_message, status=status_code)

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs) -> Response: # Frontend will send the refresh token in the request header as Bearer token and the user id in the request body to generate a new access token
        """
            Post method to generate new access token using refresh token.

            This method overrides the post method of TokenRefreshView to generate a new access token using the refresh token.
            It validates the refresh token and generates a new access token.

            Args:
                request: The request object.

            Returns:
                Response: The response object containing the new access token.
        """
        bearer = request.headers.get("Authorization")
        if not bearer or not bearer.startswith('Bearer '):
            return Response(
                {"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user_id = request.data.get("id")
            if not user_id:
                return Response({"error": "User id is required"}, status=status.HTTP_400_BAD_REQUEST)
            user_object = UserTokens.objects.filter(id=user_id).first()
            if not user_object:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            token_data = user_object.token_data
            refresh_token = bearer.split(' ')[1]
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            token_data["access"] = access_token
            user_object.token_data=token_data
            user_object.save()
        except jwt.ExpiredSignatureError:
            response_message = {"error": "User session has expired, You must login again"}
            status_code = status.HTTP_401_UNAUTHORIZED
        except Exception as err:
            return Response({"error": "Could not generate access token", "details": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"access": access_token}, status=status.HTTP_200_OK)


class ValidateToken(viewsets.ViewSet):

    def validate_token(self, access_token) -> bool:
        """
            Validate the refresh token.

            This method validates the refresh token by decoding the token and checking if it is expired.
            If the token is expired or invalid, it returns False, otherwise it returns True.

            Args:
                access_token: The refresh token to validate.

            Returns:
                bool: True if the token is valid, False otherwise.
        """
        try:
            ''' decode the token to check if it is expired
            and if it is expired, it will raise an exception
            and if it is invalid, it will raise an exception
            jwt.decode() method is used to decode the token and check if it is expired or invalid
            '''
            decoded_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_signature": True})
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def validate_token_for_user(self, request, *args, **kwargs):
        response_message = {}
        status_code = status.HTTP_200_OK
        isfrontend = request.data.get("is_frontend")
        if isfrontend is None:
            response_message, status_code = check_secret(request, response_message, status_code)
        if not response_message:
            try:
                access = request.data.get("access")
                id = request.data.get("id")
                if not access or not id:
                    response_message = {"error": "Access token and id are required"}
                    status_code = status.HTTP_400_BAD_REQUEST
                result = self.validate_token(access)
                if result:
                    user = UserTokens.objects.filter(id = id, token_data__access = access).first()
                    if user is not None:
                        response_message = {"access_token": "Valid token"}
                    else:
                        response_message = {"error": "token mismatch"}
                        status_code = status.HTTP_401_UNAUTHORIZED
                else:
                    response_message = {"error": "Invalid or expired token"}
                    status_code = status.HTTP_401_UNAUTHORIZED
            except Http404:
                response_message = {"error": "User has not logged in yet!!"}
                status_code = status.HTTP_401_UNAUTHORIZED
            except Exception as err:
                response_message = {"error": "Could not validate user access token"}
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response_message, status=status_code)

class InvalidateToken(viewsets.ViewSet):
    def invalidate_token_for_user(self, request, *args, **kwargs) -> Response: # logout endpoint will send the user id and access token in the request body to delete the user token record from the database
        response_message = {}
        status_code = status.HTTP_200_OK
        isfrontend = request.data.get("is_frontend")
        if isfrontend is None:
            response_message, status_code = check_secret(request, response_message, status_code)
        if "error" not in response_message and status_code == status.HTTP_200_OK:
            try:
                access = request.data.get("access")
                id = request.data.get("id")
                if not access or not id:
                    response_message = {"error": "Access token and id are required"}
                    status_code = status.HTTP_400_BAD_REQUEST
                else:
                    check_token = ValidateToken()
                    if check_token.validate_token(access):
                        user = get_object_or_404(UserTokens, id=id)
                        if user is not None:
                            user.delete()
                            response_message = {"detail":"User logged out"}
                    else:
                        response_message = {"error": "Invalid or expired token"}
                        status_code = status.HTTP_401_UNAUTHORIZED
            except Http404:
                response_message = {"error": "User has not logged in yet"}
                status_code = status.HTTP_401_UNAUTHORIZED
            except Exception as err:
                response_message = {"error": str(err)}
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response_message, status=status_code)
