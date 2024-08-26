# conftest.py
import pytest
from rest_framework.test import APIClient
from token_app.models import UserTokens
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import jwt


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_tokens_obj(db):
    return UserTokens.objects.create(id=1, username='testuser', token_data={})

@pytest.fixture
def user_tokens_obj_with_token(user_tokens_obj):
    refresh = RefreshToken.for_user(user_tokens_obj)
    access = refresh.access_token
    user_tokens_obj.token_data = {
        'refresh': str(refresh),
        'access': str(access)
    }
    user_tokens_obj.save()
    return user_tokens_obj

@pytest.fixture
def headers():
    headers = {
    "X-SERVICE-SECRET": settings.SECRET_KEY
    }
    return headers


@pytest.mark.django_db
def test_generate_tokens(api_client, user_tokens_obj, headers):

    url = reverse('generate_tokens')
    response = api_client.post(url, data={'id': user_tokens_obj.id, 'username': user_tokens_obj.username}, headers=headers)
    assert response.status_code == 201
    assert 'refresh' in response.data
    assert 'access' in response.data

    refresh_token = response.data['refresh']
    decoded_refresh = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
    
    assert decoded_refresh['user_id'] == user_tokens_obj.id
    assert 'exp' in decoded_refresh

    access_token = response.data['access']
    decoded_access = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])

    assert decoded_access['user_id'] == user_tokens_obj.id
    assert 'exp' in decoded_access
    assert 'token_type' in decoded_access and decoded_access['token_type'] == 'access'


# Frontend will send the refresh token in the request header as Bearer token and the user id in the request body to generate a new access token
@pytest.mark.django_db
def test_refresh_token(api_client, user_tokens_obj_with_token):
    url = reverse('token_refresh')
    refresh_token = user_tokens_obj_with_token.token_data['refresh']
    response = api_client.post(url, data={'id': user_tokens_obj_with_token.id}, headers={'Authorization': f'Bearer {refresh_token}'})
    assert response.status_code == 200
    assert 'access' in response.data

    access_token = response.data['access']
    decoded_access = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
    assert decoded_access['user_id'] == user_tokens_obj_with_token.id
    assert 'exp' in decoded_access
    assert 'token_type' in decoded_access and decoded_access['token_type'] == 'access'

@pytest.mark.django_db
def test_invalidate_token(api_client, user_tokens_obj_with_token, headers):
    url = reverse('invalidate_tokens')
    user_data = {'id': user_tokens_obj_with_token.id, 'access': user_tokens_obj_with_token.token_data['access']}
    response = api_client.post(url, data=user_data, headers=headers)
    assert response.status_code == 200
    assert response.data == {'detail': 'User logged out'}
    
    # check if the user token record is deleted from the database after invalidating the token
    with pytest.raises(UserTokens.DoesNotExist):
        user_tokens_obj_with_token.refresh_from_db() # .refresh_from_db() is used to refresh the object from the database to get the updated data

@pytest.mark.django_db
def test_validate_token(api_client, user_tokens_obj_with_token, headers):
    url = reverse('validate_token')
    user_data = {'id': user_tokens_obj_with_token.id, 'access': user_tokens_obj_with_token.token_data['access']}
    response = api_client.post(url, data=user_data, headers=headers)
    assert response.status_code == 200
    assert response.data == {'access_token': 'Valid token'}
    
    user_tokens_obj_with_token.refresh_from_db() # .refresh_from_db() is used to refresh the object from the database to get the updated data
    assert user_tokens_obj_with_token is not None # check if the user token record is still in the database