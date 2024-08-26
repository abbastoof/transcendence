# conftest.py
import pytest
from rest_framework.test import APIClient
from token_app.models import UserTokens
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

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

@pytest.mark.django_db
def test_generate_tokens(api_client, user_tokens_obj, user_tokens_obj_with_token):

    url = reverse('generate_tokens')
    response = api_client.post(url, {'id': user_tokens_obj.id, 'username': user_tokens_obj.username})
    assert response.status_code == 201
    assert response.data['refresh'] == user_tokens_obj.token_data['refresh']
    assert response.data['access'] == user_tokens_obj.token_data['access']
