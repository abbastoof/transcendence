import pytest
from rest_framework import status
from rest_framework.test import APIClient
from user_session.models import UserTokens
from django.urls import reverse

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'password': 'testpassword'
    }

@pytest.mark.django_db
def test_user_logout_valid_id(api_client):
    user = UserTokens.objects.create(id=1, username='testuser')
    assert UserTokens.objects.filter(id=1).exists()

    # Call the logout URL
    url = reverse('logout')
    response = api_client.post(url, {'id': 1}, format='json')
    assert response.status_code==200

@pytest.mark.django_db
def test_user_logout_invalid_id(api_client):
    user = UserTokens.objects.create(id=1, username='testuser')
    assert UserTokens.objects.filter(id=1).exists()

    # Call the logout URL with an invalid id
    url = reverse('logout')
    response = api_client.post(url, {'id': 2}, format='json')
    assert response.status_code==404

@pytest.mark.django_db
def test_user_logout_missing_id(api_client):
    user = UserTokens.objects.create(id=1, username='testuser')
    assert UserTokens.objects.filter(id=1).exists()

    # Call the logout URL without an id
    url = reverse('logout')
    response = api_client.post(url, format='json')
    assert response.status_code==400

@pytest.mark.django_db
def test_user_login(api_client, user_data):
    url = reverse('login')
    response = api_client.post(url, user_data, format='json')
    assert response.status_code==401