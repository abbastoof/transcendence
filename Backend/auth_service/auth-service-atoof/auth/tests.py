from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from .models import User

class AuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user = {
            'username': 'testuser',
            'password': 'testpassword'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, self.user['username']) # get() method is used to retrieve a single object from the database

    def test_user_login(self):
        User.objects.create_user(**self.user)
        response = self.client.post(self.login_url, self.user, format='json') # post() method is used to log in a user
        self.assertEqual(response.status_code, status.HTTP_200_OK)

