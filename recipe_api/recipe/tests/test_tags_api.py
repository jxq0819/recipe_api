from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTest(TestCase):
    """Test public tags APIs"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required for listing tags"""
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
