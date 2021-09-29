from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test public user APIs"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user(self):
        """Test creating a user with valid payload is successful"""
        payload = {'email': 'test@test.com', 'password': 'Password', 'name': 'Test User'}
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        """Test creating a user that already exists is failed"""
        payload = {'email': 'testexists@test.com', 'password': 'test-exists', 'name': 'Test Exists'}
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_short(self):
        """Test password must be more than 5 characters"""
        payload = {'email': 'testshort@test.com', 'password': 'pd', 'name': 'Test ShortPassword'}
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test creating a token for the user"""
        payload = {'email': 'testtoken@test.com', 'password': 'TokenTest'}
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_create_token_invalid_credentials(self):
        """Test creating a token with invalid credentials is failed"""
        payload = {'email': 'testtoken@test.com', 'password': 'WrongPassword'}
        create_user(email='testtoken@test.com', password='CorrectPassword')
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)
