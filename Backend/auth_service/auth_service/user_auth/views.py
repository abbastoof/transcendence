import json
from rest_framework import status
from auth_service import settings
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .rabbitmq_utils import consume_message, publish_message
from .serializers import CustomTokenObtainPairSerializer
import jwt

class CustomTokenObtainPairView(TokenObtainPairView):
    """
        Custom token obtain pair view to generate tokens for the user.
        
        This class inherits from TokenObtainPairView. It overrides the post method to generate tokens for the user.

        Attributes:
            serializer_class: The serializer class to use for the view.
        
        Methods:
            post: Post method to generate tokens for the user.
    
    """

    serializer_class = CustomTokenObtainPairSerializer

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
            return Response(
                {
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
            is_valid_token = ValidateToken.validate_token(refresh_token)
            if not is_valid_token:
                return Response({"error": "Session has expired"}, status=status.HTTP_401_UNAUTHORIZED)
            # If token is valid, generate a new access token
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            return Response({"access": access_token}, status=status.HTTP_200_OK)
        
        except Exception as err:
            return Response({"error": "Could not generate tokens", "details": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class ValidateToken():
    @staticmethod
    def validate_token(refresh_token) -> bool:
        """
            Validate the refresh token.

            This method validates the refresh token by decoding the token and checking if it is expired.
            If the token is expired or invalid, it returns False, otherwise it returns True.

            Args:
                refresh_token: The refresh token to validate.
            
            Returns:
                bool: True if the token is valid, False otherwise.
        """
        try:
            decoded_token = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_signature": True})
            return True
        except jwt.ExpiredSignatureError:
            print("expired token")
            return False
        except jwt.InvalidTokenError:
            print("invalid token")
            return False