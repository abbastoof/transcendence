from rest_framework import viewsets
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer
from rest_framework.response import Response
from .models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication


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
		pass

	def update_user(self, request, pk = None):
		data = get_object_or_404(User, id=pk)
		if data != request.user and not request.user.is_superuser:
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		serializer = UserSerializer(instance=data, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
		pass
	def destroy_user(self, request, pk = None):
		data = get_object_or_404(User, id=pk)
		if data != request.user and not request.user.is_superuser:
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		# Should send message to all microservices to delete all data related to this user
		data.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
		pass


class RegisterViewSet(viewsets.ViewSet):
	permission_classes = [AllowAny]

	def create_user(self, request):
		serializer = UserSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)