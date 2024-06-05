from rest_framework import viewsets
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer
from rest_framework.response import Response
from .models import User

class RegisterViewSet(viewsets.ViewSet):
	def list(self, request):
		users = User.objects.all()
		serializer = UserSerializer(users, many=True)
		return Response(serializer.data)

	def create(self, request):
		serializer = UserSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)

	def retrieve(self, request, pk = None):
		data = get_object_or_404(User, username=pk)
		serializer = UserSerializer(data)
		return Response(serializer.data)


	def update(self, request, pk = None):
		data = get_object_or_404(User, username=pk)
		serializer = UserSerializer(instance=data, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

	def destroy(self, request, pk = None):
		data = get_object_or_404(User, username=pk)
		data.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
