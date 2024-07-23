import pytest
import json
from django.urls import reverse
from unittest.mock import patch, MagicMock
from rest_framework_simplejwt.tokens import RefreshToken
from user_app.views import UserViewSet, RegisterViewSet, FriendsViewSet, validate_token
from user_app.user_session_views import UserLoginView, UserLogoutView
from rest_framework import status
from user_app.models import UserProfileModel

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
    return UserProfileModel.objects.create_user(username='testuser', email='testuser@123.com', password='Test@123')

@pytest.fixture
def admin_user(db):
    return UserProfileModel.objects.create_superuser(username='admin', email='admin@123.com', password='Admin@123')

@pytest.fixture
def user_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

@pytest.fixture
def admin_token(admin_user):
    refresh = RefreshToken.for_user(admin_user)
    return str(refresh.access_token)

@pytest.fixture
def mock_rabbitmq():
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
        yield mock_publish, mock_consume

@pytest.mark.django_db
def test_users_list(api_client, admin_user, admin_token, user_data, mock_rabbitmq):
    # Mock the RabbitMQ interactions
    user1 = UserProfileModel.objects.create_user(username='testuser1',email='testuser1@123.com',password='Test@123')
    user2 = UserProfileModel.objects.create_user(username='testuser2',email='testuser2@123.com',password='Test@123')

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
    print("response_data", response.data)
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
        assert response.status_code == 200
        assert response.data["detail"] == 'User logged out successfully'
        assert UserProfileModel.objects.filter(username=admin_user.username).exists()

@pytest.mark.django_db
def test_retrieve_user(api_client, user, user_token, mock_rabbitmq):
        # Authenticate the request
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

    url = reverse('user-detail', kwargs={'pk': user.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user.id
    assert response.data['username'] == user.username
    assert response.data['email'] == user.email

@pytest.mark.django_db
def test_update_user(api_client, user, user_token, mock_rabbitmq):
    data = {
        "username": "newuser",
        "email": "newuser@123.com"
    }
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

    url = reverse('user-detail', kwargs={'pk': user.id})
    response = api_client.put(url, data, format='json')

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data['id'] == user.id
    assert response.data['username'] == 'newuser'
    assert response.data['email'] == 'newuser@123.com'

def test_destroy_user(api_client, user, user_token, mock_rabbitmq):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

    url = reverse('user-detail', kwargs={'pk': user.id}) # Get the URL for the user object to be deleted
    response = api_client.delete(url) # Call the API endpoint to delete the user object and assert the response status code

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not UserProfileModel.objects.filter(username=user.username).exists()

@pytest.mark.django_db
def test_valid_data_friend_request_functions(api_client, admin_user, user, user_token, admin_token, mock_rabbitmq):

    print("\ntestuser sends a friend request to admin user")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('friends-request', kwargs={'user_pk': user.id, 'pk':admin_user.id})
    response_request = api_client.post(url_request, format='json')
    assert response_request.status_code == status.HTTP_201_CREATED
    assert response_request.data["detail"]=='Friend request sent'

    print("\nAdmin check the friend requests list")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('friend_request-list', kwargs={'user_pk': admin_user.id})
    response_request = api_client.get(url_request, format='json')
    assert response_request.data[0]["sender_user"] == 11
    assert response_request.data[0]["receiver_user"] == 10
    assert response_request.data[0]["status"] == 'pending'
    assert response_request.status_code == status.HTTP_200_OK

    print("\nAdmin accept the friend request")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('friends-request', kwargs={'user_pk': admin_user.id, 'pk':user.id})
    response_request = api_client.put(url_request, format='json')
    assert response_request.data["detail"]=='Request accepted'
    assert response_request.status_code == status.HTTP_202_ACCEPTED

    print("\nAdmin user has testuser in its friends list")
    url_request = reverse('friends-list', kwargs={'user_pk': admin_user.id})
    response_request = api_client.get(url_request, format='json')
    assert response_request.data[0]["username"] == "testuser"

    print("\ntest user has admin in its friends list")
    url_request = reverse('friends-list', kwargs={'user_pk': user.id})
    response_request = api_client.get(url_request, format='json')
    assert response_request.data[0]["username"] == "admin"
    assert response_request.status_code == 200

    print("\ntestuser delete the admin user from its friends list")
    url_request = reverse('remove-friend', kwargs={'user_pk': user.id, 'pk': admin_user.id})
    response_request = api_client.delete(url_request, format='json')
    assert response_request.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_send_friend_request_invalid_user_id(api_client, admin_user, user, user_token, admin_token, mock_rabbitmq):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

    url_request = reverse('friends-request', kwargs={'user_pk': user.id, 'pk':2})
    response_request = api_client.post(url_request, format='json')
    assert response_request.status_code == 404
    assert response_request.data["error"]=="User does not exist"

@pytest.mark.django_db
def test_reject_friend_request(api_client, admin_user, user, user_token, admin_token, mock_rabbitmq):

    print("\ntestuser sends a friend request to admin user")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('friends-request', kwargs={'user_pk': user.id, 'pk':admin_user.id})
    response_request = api_client.post(url_request, format='json')
    assert response_request.status_code == status.HTTP_201_CREATED
    assert response_request.data["detail"]=='Friend request sent'

    print("\nAdmin check the friend requests list")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('friend-request-list', kwargs={'user_pk': admin_user.id})
    response_request = api_client.get(url_request, format='json')
    assert response_request.data[0]["sender_user"] == 15
    assert response_request.data[0]["receiver_user"] == 14
    assert response_request.data[0]["status"] == 'pending'
    assert response_request.status_code == status.HTTP_200_OK

    print("Admin reject the testuser request")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('reject-request', kwargs={'user_pk': admin_user.id,'pk':user.id})
    response_request = api_client.put(url_request, format='json')
    assert response_request.data["detail"] == "Request rejected"
    assert response_request.status_code == status.HTTP_202_ACCEPTED
