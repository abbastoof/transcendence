from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from .rabbitmq_utils import publish_message, consume_message
import json
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


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
			refresh = RefreshToken.for_user(user_data['username'])
			access_token = str(refresh.access_token)
			return Response({
				'refresh': str(refresh),
				'access': str(access_token)
				}, status=status.HTTP_200_OK)
