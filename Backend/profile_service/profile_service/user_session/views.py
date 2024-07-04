from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .rabbitmq_utils import publish_message, consume_message
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserTokenModelSerializer
from .models import UserTokens
from profile_service import settings
import jwt
import json

# Create your views here.
class UserSessionViewClass(viewsets.ViewSet):
    def login(self, request, *args, **kwargs) -> Response:
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
            "login_request_queue",
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
        consume_message("login_response_queue", handle_response)

        # Wait for the response to be processed
        if "error" in user_data:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            user = UserTokens.objects.get(id=user_data["id"])
            serializer = UserTokenModelSerializer(user).data.copy()
            response_messsage = {"id": serializer["id"],
                            "refresh":serializer["token_data"]["refresh"],
                            "access":serializer["token_data"]["access"]}
        except UserTokens.DoesNotExist:
            publish_message("user_token_request_queue", json.dumps({"username": username}))

            user_token_data = {}

            def handle_token_response(ch, method, properties, body):
                nonlocal user_token_data
                user_token_data.update(json.loads(body))
                ch.stop_consuming()
            
            consume_message("user_token_response_queue", handle_token_response)

            if "error" in user_token_data:
                return Response(
                    {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
                )
            
            response_messsage = {"id": user_data["id"], 
                            "refresh":user_token_data["refresh"],
                            "access":user_token_data["access"]}

            serializer = UserTokenModelSerializer(data={
                "id": user_data["id"],
                "username": username,
                "token_data": {
                "refresh": user_token_data["refresh"],
                "access": user_token_data["access"]}
            })

            if serializer.is_valid():
                serializer.save()            
        return Response(response_messsage, status=status.HTTP_200_OK)
        

    def logout(self, request, *args, **kwargs) -> Response:
        """
            Post method to delete the user tokens.

            This method deletes the user tokens from the database.

            Args:
                request: The request object.
            
            Returns:
                Response: The response object containing the message.
        """
        if not request.data.get("id"):
            return Response(
                {"error": "User id is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        user_id = request.data.get("id")
        user = get_object_or_404(UserTokens, id=user_id)
        user.delete()
        return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
    

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
            print("expired token")
            return False
        except jwt.InvalidTokenError:
            print("invalid token")
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
        try:
            is_valid = self.validate_token(access_token)
            user = get_object_or_404(UserTokens, token_data__access=access_token)
            response = {"access token is valid": is_valid}
            publish_message("validate_token_response_queue", json.dumps(response))
        except Exception as e:
            publish_message("validate_token_response_queue", json.dumps({"error": str(e)}))

    def start_consumer(self) -> None:
        consume_message("validate_token_request_queue", self.validate_token_request_queue)