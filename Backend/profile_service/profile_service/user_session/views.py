from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rabbitmq_utils import publish_message, consume_message
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserTokens
import json

# Create your views here.
class LoginViewClass(ViewSet):
    def post(self, request, *args, **kwargs) -> Response:
        """
            Post method to generate tokens for the user.

            This method overrides the post method of TokenObtainPairView to generate tokens for the user. 
            It sends a request to the user service to validate the user credentials
            and get the user data. It then generates the tokens for the user and returns the tokens in the response.

            Args:
                request: The request object.
            
            Returns:
                Response: The response object containing the tokens.
        """

        username = request.data.get("username")
        password = request.data.get("password")

        # Send request to user service
        publish_message(
            "user_request_queue",
            json.dumps({"username": username, "password": password}),
        )

        # This will store the response from user service
        user_data = {}

        # Define a callback function to process the message
        def handle_response(ch, method, properties, body):
            nonlocal user_data
            user_data.update(json.loads(body))
            ch.stop_consuming()

        # Start consuming the response
        consume_message("auth_response_queue", handle_response)

        # Wait for the response to be processed
        if "error" in user_data:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            user = type("User", (object,), user_data)  # Mock user object with user_data
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            # Save the updated or newly created UserTokens entry
            user_token_entry, created = UserTokens.objects.get_or_create(
                id=user_data["id"], username=username
            )
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            user_token_entry.token_data = {
                "refresh": {
                    "token": str(refresh),
                    "exp": int(refresh["exp"]),  # Store expiration as integer
                },
                "access": {
                    "token": str(access),
                    "exp": int(access["exp"]),  # Store expiration as integer
                },
            }

            # Save the updated or newly created UserTokens entry
            user_token_entry.save()

            return Response(
                {
                    "id": user_data["id"],
                    "refresh": str(refresh),
                    "access": str(access),
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": "Could not generate tokens", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
