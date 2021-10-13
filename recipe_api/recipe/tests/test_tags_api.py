from core.models import Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTest(TestCase):
    """Test public tags APIs"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required for listing tags"""
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test private tags APIs"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(email='test@test.com', password='tesTTest321')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_tags(self):
        """Test listing tags"""
        Tag.objects.create(user=self.user, name='Low fat')
        Tag.objects.create(user=self.user, name='Gluten free')

        response = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test listed tags limited to the authenticated user"""
        user2 = get_user_model().objects.create_user(email='another@test.com', password='AnotherTest')
        Tag.objects.create(user=user2, name='Seafood')
        tag = Tag.objects.create(user=self.user, name='Organic')
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_create_tag(self):
        """Test creating a new tag"""
        payload = {'name': 'Test tag'}
        response = self.client.post(TAGS_URL, payload)
        tag_exists = Tag.objects.filter(user=self.user, name=payload['name'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(tag_exists)
