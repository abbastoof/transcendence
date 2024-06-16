from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .rabbitmq_utils import publish_message, consume_message
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,timezone
from .models import UserTokens
import json

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	@classmethod
	def get_token(cls, user):
		token = super().get_token(user)
		token['custom_claims'] = {'username': user.username, 'password': user.password}
		return token

class CustomTokenObtainPairView(TokenObtainPairView):
	serializer_class = CustomTokenObtainPairSerializer

	def post(self, request, *args, **kwargs):
		username = request.data.get('username')
		password = request.data.get('password')

		# Send request to user service
		publish_message('user_request_queue', json.dumps({'username': username, 'password': password}))

		# This will store the response from user service
		user_data = {}

		# Define a callback function to process the message
		def handle_response(ch, method, properties, body):
			nonlocal user_data
			user_data.update(json.loads(body))
			ch.stop_consuming()

		# Start consuming the response
		consume_message('auth_response_queue', handle_response)

		# Wait for the response to be processed
		if 'error' in user_data:
			return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
		try:
			user = type('User', (object,), user_data)  # Mock user object with user_data
			refresh = None
			access = None

			# Retrieve or create the UserTokens entry
			user_token_entry, created = UserTokens.objects.get_or_create(username=username)

			if not created:
				# If the user entry already exists, check if tokens are still valid
				token_data = user_token_entry.token_data
				refresh_expire_time = token_data['refresh']['exp']
				access_expire_time = token_data['access']['exp']
				refresh = RefreshToken(token_data['refresh']['token'])
				access = token_data['access']['token']
				current_time = datetime.now(timezone.utc)
				if refresh_expire_time < current_time.timestamp() or access_expire_time < current_time.timestamp():	
					if refresh_expire_time < current_time.timestamp():
						refresh = RefreshToken.for_user(user)
						access = refresh.access_token
					elif access_expire_time < current_time.timestamp():
						refresh = RefreshToken(token_data['refresh']['token'])
						access = refresh.access_token
					user_token_entry.token_data = {
						'refresh': {
							'token': str(refresh),
							'exp': int(refresh['exp']),  # Store expiration as integer
						},
						'access': {
							'token': str(access),
							'exp': int(access['exp']),  # Store expiration as integer
						}
					}
			else:
				# If the user entry was just created, store new tokens
				refresh = RefreshToken.for_user(user)
				access = refresh.access_token
				user_token_entry.token_data = {
					'refresh': {
						'token': str(refresh),
						'exp': int(refresh['exp']),  # Store expiration as integer
					},
					'access': {
						'token': str(access),
						'exp': int(access['exp']),  # Store expiration as integer
					}
				}

			# Save the updated or newly created UserTokens entry
			user_token_entry.save()

			return Response({
				'refresh': str(refresh),
				'access': str(access),
			}, status=status.HTTP_200_OK)

		except Exception as e:
			return Response({'error': 'Could not generate tokens', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
