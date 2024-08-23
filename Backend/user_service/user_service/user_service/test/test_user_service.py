import pytest
import json
from django.urls import reverse
from unittest.mock import patch, MagicMock
from rest_framework_simplejwt.tokens import RefreshToken
from user_app.views import UserViewSet, RegisterViewSet, FriendsViewSet, validate_token
from user_app.user_session_views import UserLoginView, UserLogoutView
from rest_framework import status
from user_app.models import UserProfileModel, ConfirmEmail
from user_app.serializers import UserSerializer
import os
from dotenv import load_dotenv
from django.conf import settings

headers = {
    "X-SERVICE-SECRET": settings.SECRET_KEY
}

load_dotenv()
TOEKNSERVICE = os.environ.get('TOKEN_SERVICE')

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

def admin_data():
    return {
        'id': 1,
        'username': 'adminuser',
        'email': 'adminuser@123.com',
        'password': 'Admin@123'
    }

@pytest.fixture
def user(db):
    email_obj = ConfirmEmail.objects.create(user_email = 'testuser@123.com', verify_status = True)
    user_serializer = UserSerializer(data = {"username":'testuser', "email":email_obj.pk, "password":'Test@123'})
    user_serializer.is_valid(raise_exception=True)
    user_serializer.save()
    return UserProfileModel.objects.get(username='testuser')

@pytest.fixture
def admin_user(db):
    admin_email = ConfirmEmail.objects.create(user_email = 'admintest@123.com', verify_status = True)
    user_obj = UserSerializer(data = {"username":'adminuser', "email":admin_email.pk, "password":'Admin@123'})
    user_obj.is_valid(raise_exception=True)
    user_obj.save()
    return UserProfileModel.objects.get(username='adminuser')

@pytest.fixture
def user_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

@pytest.fixture
def admin_token(admin_user):
    refresh = RefreshToken.for_user(admin_user)
    return str(refresh.access_token)

@pytest.fixture(autouse=True)
def mock_validate_token():
    with patch('user_app.views.validate_token', return_value=True):
        yield

@pytest.mark.django_db
def test_user_register(api_client, user_data):
    email_obj = ConfirmEmail.objects.create(user_email = 'testuser@123.com', verify_status = True)
    url = reverse('user-register')
    user_data["email"] = email_obj.pk
    response = api_client.post(url, user_data, format='json')
    assert response.status_code == 201
    assert response.data['id'] == 1
    assert response.data['username'] == 'testuser'
    assert response.data['email'] == 'testuser@123.com'

@pytest.mark.django_db
def test_users_list(api_client, admin_user, admin_token):
    # Mock the RabbitMQ interactions
    email1_obj = ConfirmEmail.objects.create(user_email = 'testuser1@123.com', verify_status = True)
    user1 = UserSerializer(data = {'username':'testuser1','email' : email1_obj.pk,'password':'Test@123'})
    user1.is_valid(raise_exception=True)
    user1.save()
    email2_obj = ConfirmEmail.objects.create(user_email = 'testuser2@123.com', verify_status = True)
    user2 = UserSerializer(data = {'username':'testuser2','email' : email2_obj.pk,'password':'Test@123'})
    user2.is_valid(raise_exception=True)
    user2.save()

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
        "username":"adminuser",
        "password":"Admin@123"
    }
    url = reverse("user-login")
    response = api_client.post(url, data, format='json')
    print("response_data", response.data)
    assert response.status_code == 200

@pytest.mark.django_db
@patch('user_app.user_session_views.requests.post')
def test_user_logout(mock_post, api_client, admin_user, admin_token):
    # Authenticate the request
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"detail": "User logged out successfully"}
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')

    url = reverse('user-logout', kwargs={'pk': admin_user.id})
    response = api_client.post(url)
    assert response.status_code == 200
    assert response.data["detail"] == 'User logged out successfully'
    mock_post.assert_called_once_with(
        f"{TOEKNSERVICE}/auth/token/invalidate-tokens/",
        data={"access": admin_token, 'id':admin_user.id}, headers=headers
    )
    assert UserProfileModel.objects.filter(username=admin_user.username).exists()

@pytest.mark.django_db
def test_retrieve_user(api_client, user, user_token):
        # Authenticate the request
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

    url = reverse('user-detail', kwargs={'pk': user.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user.id
    assert response.data['username'] == user.username
    assert response.data['email'] == user.email.user_email

@pytest.mark.django_db
def test_update_user(api_client, user, user_token):
    email_obj = ConfirmEmail.objects.create(user_email = "newuser@123.com", verify_status=True)
    data = {
        "username": "newuser",
        "email": email_obj.pk
    }
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

    url = reverse('user-detail', kwargs={'pk': user.id})
    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data['id'] == user.id
    assert response.data['username'] == 'newuser'
    assert response.data['email'] == 'newuser@123.com'

def test_destroy_user(api_client, user, user_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

    url = reverse('user-detail', kwargs={'pk': user.id}) # Get the URL for the user object to be deleted
    response = api_client.delete(url) # Call the API endpoint to delete the user object and assert the response status code

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not UserProfileModel.objects.filter(username=user.username).exists()

@pytest.mark.django_db
def test_valid_data_friend_request_functions(api_client, admin_user, user, user_token, admin_token):

    print("\ntestuser sends a friend request to admin user")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('send-request', kwargs={'user_pk': user.id})
    response_request = api_client.post(url_request, data={'username': 'adminuser'}, format='json')
    assert response_request.status_code == status.HTTP_201_CREATED
    assert response_request.data["detail"]=='Friend request sent'

    print("\nAdmin check the friend requests list")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('friend-request-list', kwargs={'user_pk': admin_user.id})
    response_request = api_client.get(url_request, format='json')
    assert response_request.data[0]["sender_username"] == 'testuser'
    assert response_request.data[0]["receiver_username"] == 'adminuser'
    assert response_request.data[0]["status"] == 'pending'
    assert response_request.status_code == status.HTTP_200_OK

    print("\nAdmin accept the friend request")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('accept-request', kwargs={'user_pk': admin_user.id, 'pk':user.id})
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
    assert response_request.data[0]["username"] == "adminuser"
    assert response_request.status_code == 200

    print("\ntestuser delete the admin user from its friends list")
    url_request = reverse('remove-friend', kwargs={'user_pk': user.id, 'pk': admin_user.id})
    response_request = api_client.delete(url_request, format='json')
    assert response_request.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_send_friend_request_invalid_user_id(api_client, admin_user, user, user_token, admin_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

    url_request = reverse('send-request', kwargs={'user_pk': user.id})
    response_request = api_client.post(url_request, data={'username':'invalid_user'}, format='json')
    assert response_request.status_code == 404
    assert response_request.data["error"]=="User does not exist"

@pytest.mark.django_db
def test_reject_friend_request(api_client, admin_user, user, user_token, admin_token):

    print("\ntestuser sends a friend request to admin user")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('send-request', kwargs={'user_pk': user.id})
    response_request = api_client.post(url_request, {'username': 'adminuser'}, format='json')
    assert response_request.status_code == status.HTTP_201_CREATED
    assert response_request.data["detail"]=='Friend request sent'

    print("\nAdmin check the friend requests list")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('friend-request-list', kwargs={'user_pk': admin_user.id})
    response_request = api_client.get(url_request, format='json')
    assert response_request.data[0]["sender_username"] == 'testuser'
    assert response_request.data[0]["receiver_username"] == 'adminuser'
    assert response_request.data[0]["status"] == 'pending'
    assert response_request.status_code == status.HTTP_200_OK

    print("Admin reject the testuser request")
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    url_request = reverse('reject-request', kwargs={'user_pk': admin_user.id,'pk':user.id})
    response_request = api_client.put(url_request, format='json')
    assert response_request.data["detail"] == "Request rejected"
    assert response_request.status_code == status.HTTP_202_ACCEPTED
