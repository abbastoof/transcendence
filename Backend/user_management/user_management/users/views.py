from rest_framework import viewsets
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import Http404
from .serializers import UserSerializer
from rest_framework.response import Response
from .models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .rabbitmq_utils import publish_message, consume_message
from django.contrib.auth import authenticate
import json


class UserViewSet(viewsets.ViewSet):
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]

	def users_list(self, request):
		if not request.user.is_staff or not request.user.is_superuser:
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		users = User.objects.all()
		serializer = UserSerializer(users, many=True)
		return Response(serializer.data)

	def retrieve_user(self, request, pk = None):
		data = get_object_or_404(User, id=pk)
		serializer = UserSerializer(data)
		return Response(serializer.data)


	def update_user(self, request, pk = None):
		data = get_object_or_404(User, id=pk)
		if data != request.user and not request.user.is_superuser:
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		serializer = UserSerializer(instance=data, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		# if User updated Username should send message to all microservices to update the username related to this user using Kafka
		serializer.save()
		return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

	def destroy_user(self, request, pk = None):
		data = get_object_or_404(User, id=pk)
		if data != request.user and not request.user.is_superuser:
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		# Should send message to all microservices to delete all data related to this user using Kafka
		data.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

	@staticmethod
	@method_decorator(csrf_exempt)
	def handle_rabbitmq_request(ch, method, properties, body):
		payload = json.loads(body)
		username = payload.get('username')
		password = payload.get('password')

		# Authenticate the user
		user = authenticate(username=username, password=password)
		
		if user is not None:
			# Check if the user is active
			if user.is_active and not user.is_staff:
				serializer = UserSerializer(user)
				response_message = serializer.data
			else:
				response_message = {"error": "User is inactive or staff"}
		else:
			response_message = {"error": "Invalid username or password"}
		print(f"Response message: {response_message}")
		publish_message('auth_response_queue', json.dumps(response_message))


	def start_consumer(self):
		consume_message('user_request_queue', self.handle_rabbitmq_request)


class RegisterViewSet(viewsets.ViewSet):
	permission_classes = [AllowAny]

	def create_user(self, request):
		serializer = UserSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)