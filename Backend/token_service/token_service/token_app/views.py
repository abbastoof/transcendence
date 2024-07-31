import json
import logging
from django.http import Http404
from rest_framework import status
from token_service import settings
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .rabbitmq_utils import consume_message, publish_message
from .serializers import CustomTokenObtainPairSerializer
from .models import UserTokens
import jwt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
        CustomTokenObtainPairView class to handle token request.

        This class inherits from TokenObtainPairView. It defines the method to handle the token request.

        Methods:
            handle_token_request: Method to handle the token request.
            start_consumer: Method to start the RabbitMQ consumer.
    """
    serializer_class = CustomTokenObtainPairSerializer
    @staticmethod
    @method_decorator(csrf_exempt)
    def handle_token_request(ch, method, properties, body):
        """
            Method to handle the token request.

            This method processes the token request message received from the user service.
            It publishes the token data to the user token request queue.

            Args:
                ch: The channel object.
                method: The method object.
                properties: The properties object.
                body: The body of the message.
        """
        data = json.loads(body)
        username = data.get("username")
        id = data.get("id")
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
                    refresh = RefreshToken(token_data["refresh"])
                    token_data["access"] = str(refresh.access_token)
                    user.token_data = token_data
                    user.save()
                    response_message = {
                        "id": id,
                        "refresh": str(refresh),
                        "access": token_data["access"]
                    }
                except jwt.ExpiredSignatureError:
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
                except Exception as err:
                    response_message = {"error": str(err)}
        except Exception as err:
            response_message = {"error": str(err)}
        publish_message("user_token_response_queue", json.dumps(response_message))


    def start_consumer(self) -> None:
        consume_message("user_token_request_queue", self.handle_token_request)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs) -> Response:
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
            refresh_token = bearer.split(' ')[1]
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access": access_token}, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({"error": "Could not generate access token", "details": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidateToken():
    @staticmethod
    def validate_token(access_token) -> bool:
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
            decoded_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_signature": True})
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def validate_token_request_queue(self, ch, method, properties, body):
        """
            Method to handle the token validation request.

            This method processes the token validation request message received from the user service.
            It validates the access token and sends the response back to the user service.

            Args:
                ch: The channel object.
                method: The method object.
                properties: The properties object.
                body: The body of the message.
        """
        data = json.loads(body)
        access_token = data.get("access")
        id = data.get("id")
        response = {}
        try:
            result = self.validate_token(access_token)
            if result:
                logger.info("result= %s", result)
                user = UserTokens.objects.filter(id = id, token_data__access = access_token).first()

                logger.info("user.username= %s", user.username)
                logger.info("user.token_data['access']= %s", user.token_data["access"])
                if result:
                    response = {"access_token": "Valid token"}
                else:
                    response = {"error": "token mismatch"}
        except jwt.ExpiredSignatureError:
            response = {"error": "token is expired"}
        except jwt.InvalidTokenError:
            response = {"error": "Invalid token"}
        except Http404:
            response = {"error": "User has not logged in yet!!"}
        except Exception as err:
            response = {"error": str(err)}
        logger.info("response = %s", response)
        publish_message("validate_token_response_queue", json.dumps(response))

    def start_consumer(self) -> None:
        consume_message("validate_token_request_queue", self.validate_token_request_queue)

class InvalidateToken():
    @staticmethod
    @method_decorator(csrf_exempt)
    def handle_logout_request_queue(ch, method, properties, body):
        data = json.loads(body)
        access = data.get("access")
        id = data.get("id")
        response_message={}
        try:
            if ValidateToken.validate_token(access):
                user = get_object_or_404(UserTokens, id=id)
                if user is not None:
                    user.delete()
                    response_message = {"detail":"User logged out"}
        except jwt.ExpiredSignatureError:
            response_message = {"error": "Access token is expired"}
        except jwt.InvalidTokenError:
            response_message = {"error": "Invalid access token"}
        except Http404:
            response_message = {"error": "User has not logged in yet"}
        except Exception as err:
            response_message = {"error": str(err)}
        publish_message("logout_response_queue", json.dumps(response_message))

    def start_consumer(self):
        consume_message("logout_request_queue", self.handle_logout_request_queue)