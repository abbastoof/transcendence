from rest_framework import generics
from django.contrib.auth import authenticate
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from django.contrib.auth import logout

class RegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer

class LoginView(generics.GenericAPIView):
	serializer_class = UserSerializer

	def post(self, request, *args, **kwargs): # post method is used to log in a user
		username = request.data.get('username')
		password = request.data.get('password')
		user = authenticate(username=username, password=password)
		if user:
			return Response({'message': 'Login successful'})
		return Response({'message': 'Login failed'}, status=401)

	def logoutUser(self, request):
		logout(request)
		return Response({'message': 'Logout successful'})

