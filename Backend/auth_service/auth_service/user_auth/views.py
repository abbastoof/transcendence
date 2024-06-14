from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .rabbitmq_utils import publish_message, consume_message
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
import json

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	@classmethod
	def get_token(cls, user):
		token = super().get_token(user)
		token['custom_claims'] = {'username': user.username, 'password': user.password}
		return token


class CustomTokenObtainPairView(TokenObtainPairView):
	def post(self, request, *args, **kwargs):
		username = request.data.get('username')
		password = request.data.get('password')
		
		# Send request to user service
		publish_message('user_request_queue', json.dumps({'username': username, 'password': password}))
		
		# This will store the response from user service
		user_data = None

		# Define a callback function to process the message
		def handle_response(ch, method, properties, body):
			nonlocal user_data
			user_data = json.loads(body)
			ch.stop_consuming()

		# Start consuming the response
		consume_message('auth_response_queue', handle_response)

		# Wait for the response to be processed
		while user_data is None:
			pass  # Busy wait for response
		if 'error' in user_data:
			return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
		else:
			try:
				# Directly use the serializer to generate tokens
				serializer = self.serializer_class(data={}, context={'request': request})
				serializer.is_valid(raise_exception=True)
				refresh = serializer.validated_data['refresh']
				access = serializer.validated_data['access']
				print(f"Access token: {str(access)}")
				print(f"Refresh token: {str(refresh)}")
				return Response({'access': access, 'refresh': str(refresh)}, status=status.HTTP_200_OK)
			except Exception as e:
				return Response({'error': 'Could not generate tokens'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
