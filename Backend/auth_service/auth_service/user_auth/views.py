import json
from rest_framework import status
from auth_service import settings
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
        user = type('User', (object,), {"id": 1, "username": username})
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        publish_message("user_token_response_queue", json.dumps({"refresh": str(refresh), "access": access_token}))

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