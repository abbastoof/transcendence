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
from .models import User
from .rabbitmq_utils import consume_message, publish_message
from .serializers import UserSerializer

class UserSession(viewsets.ViewSet):
    authentication_classes = [AllowAny]

    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if username and password:
            user = authenticate(username=username, password=username)
            if user is not None:
                if user.is_active:
                    serializer = UserSerializer(user, data={"status": True}, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    response_message = {"id": serializer.data["id"], "username": serializer.data["username"]}
                    response_message = self.publish_and_consume(response_message, serializer.data)
                    status_code = status.HTTP_200_OK
                else:
                    response_message = {"detail": "User is inactive"}
                    status_code = status.HTTP_401_UNAUTHORIZED
            else:
                response_message = {"detail": "Invalid username or password"}
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            response_message = {"detail": "Username or password is missing"}
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(response_message, status=status_code)

    def publish_and_consume(response_message, user_data) -> dict:
        publish_message("user_token_request_queue", json.dumps(response_message))
        user_token_data = {}

        def handle_token_response(ch, method, properties, body):
            nonlocal user_token_data
            user_token_data.update(json.loads(body))
            ch.stop_consuming()

        consume_message("user_token_response_queue", handle_token_response)

        if "error" in user_token_data:
            response_message = {"error": "Invalid credentials", "status":status.HTTP_401_UNAUTHORIZED}
        else:
            response_message = {"id": user_data.data["id"],
                        "refresh":user_token_data["refresh"],
                        "access":user_token_data["access"]}
        return response_message
        