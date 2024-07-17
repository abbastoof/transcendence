import pytest
import json
from django.urls import reverse
from unittest.mock import patch, MagicMock
from rest_framework_simplejwt.tokens import RefreshToken
from user_app.views import UserViewSet, RegisterViewSet, FriendsViewSet, validate_token
from user_app.user_session_views import UserLoginView, UserLogoutView
from rest_framework import status
from user_app.models import User

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user_data():
    return {
        'id': 1,
        'username': 'testuser',
        'email': 'testuser@123.com',
        'password': 'Test@123'
    }

@pytest.mark.django_db
def test_user_register(api_client, user_data):
    url = reverse('register-user')
    response = api_client.post(url, user_data, format='json')
    assert response.status_code == 201
    assert response.data['id'] == 1
    assert response.data['username'] == 'testuser'
    assert response.data['email'] == 'testuser@123.com'


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', email='testuser@123.com', password='Test@123')

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(username='admin', email='admin@123.com', password='Admin@123')

@pytest.fixture
def user_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

@pytest.fixture
def admin_token(admin_user):
    refresh = RefreshToken.for_user(admin_user)
    return str(refresh.access_token)

@pytest.mark.django_db
def test_users_list(api_client, admin_user, admin_token, user_data):
    # Mock the RabbitMQ interactions
    user1 = User.objects.create_user(username='testuser1',email='testuser1@123.com',password='Test@123')
    user2 = User.objects.create_user(username='testuser2',email='testuser2@123.com',password='Test@123')
    with patch('user_app.views.publish_message') as mock_publish, patch('user_app.views.consume_message') as mock_consume:
        # Set up the mock for consume_message to simulate a valid token response
        def mock_consume_response(queue_name, callback):
            response_data = json.dumps({"is_valid": True})
            ch_mock = MagicMock()
            method = None
            properties = None
            body = response_data.encode('utf-8')
            callback(ch_mock, method, properties, body)

        mock_consume.side_effect = mock_consume_response

        # Authenticate the request
        token = admin_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Call the API endpoint
        url = reverse('users-list')  # Ensure this matches your URL configuration
        response = api_client.get(url)

        # Assert the response status and content
        print("response data=", response.data)
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_user_login(api_client, admin_user):
    data = {
        "username":"admin",
        "password":"Admin@123"
    }
    url = reverse("user-login")
    response = api_client.post(url, data, format='json')
    print("response = ", response)
    assert response.status_code == 200

@pytest.mark.django_db
def test_user_logout(api_client, admin_user, admin_token):
    with patch('user_app.user_session_views.publish_message') as mock_publish, patch('user_app.user_session_views.consume_message') as mock_consume:
        # Set up the mock for consume_message to simulate a valid token response
        def mock_consume_response(queue_name, callback):
            response_data = json.dumps({"is_valid": True})
            ch_mock = MagicMock()
            method = None
            properties = None
            body = response_data.encode('utf-8')
            callback(ch_mock, method, properties, body)

        mock_consume.side_effect = mock_consume_response

            # Authenticate the request
        token = admin_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('user-logout', kwargs={'pk': admin_user.id})
        response = api_client.post(url)
        print("response = ", response)
        assert response.status_code == 200
        assert User.objects.filter(username=admin_user.username).exists()

@pytest.mark.django_db
def test_retrieve_user(api_client, user, user_token):
    with patch('user_app.views.publish_message') as mock_publish, patch('user_app.views.consume_message') as mock_consume:
        # Set up the mock for consume_message to simulate a valid token response
        def mock_consume_response(queue_name, callback):
            response_data = json.dumps({"is_valid": True})
            ch_mock = MagicMock()
            method = None
            properties = None
            body = response_data.encode('utf-8')
            callback(ch_mock, method, properties, body)

        mock_consume.side_effect = mock_consume_response

        # Authenticate the request
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

        url = reverse('user-detail', kwargs={'pk': user.id})
        response = api_client.get(url)

        print("response data=", response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email

@pytest.mark.django_db
def test_update_user(api_client, user, user_token):
    data = {
        "username": "newuser",
        "email": "newuser@123.com"
    }
    with patch('user_app.views.publish_message') as mock_publish, patch('user_app.views.consume_message') as mock_consume:
        # Set up the mock for consume_message to simulate a valid token response
        def mock_consume_response(queue_name, callback):
            response_data = json.dumps({"is_valid": True})
            ch_mock = MagicMock()
            method = None
            properties = None
            body = response_data.encode('utf-8')
            callback(ch_mock, method, properties, body)

        mock_consume.side_effect = mock_consume_response # Authenticate the request, .side_effect is used to set the return value of the mock object

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

        url = reverse('user-detail', kwargs={'pk': user.id})
        response = api_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data['id'] == user.id
        assert response.data['username'] == 'newuser'
        assert response.data['email'] == 'newuser@123.com'

def test_destroy_user(api_client, user, user_token):
    with patch('user_app.views.publish_message') as mock_publish, patch('user_app.views.consume_message') as mock_consume:
        # Set up the mock for consume_message to simulate a valid token response
        def mock_consume_response(queue_name, callback):
            response_data = json.dumps({"is_valid": True})
            ch_mock = MagicMock()
            method = None
            properties = None
            body = response_data.encode('utf-8')
            callback(ch_mock, method, properties, body) # callback is called with the mock objects and the response data to simulate the response

        mock_consume.side_effect = mock_consume_response # Authenticate the request using the user token and call the API endpoint to delete the user object

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

        url = reverse('user-detail', kwargs={'pk': user.id}) # Get the URL for the user object to be deleted
        response = api_client.delete(url) # Call the API endpoint to delete the user object and assert the response status code

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(username=user.username).exists()
