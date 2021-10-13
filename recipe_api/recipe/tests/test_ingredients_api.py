from core.models import Ingredient
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTest(TestCase):
    """Test public ingredients APIs"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required for listing ingredients"""
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    """Test private ingredients APIs"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='test@test.com', password='testIngredient')
        self.client.force_authenticate(self.user)

    def test_list_ingredients(self):
        """Test listing ingredients"""
        Ingredient.objects.create(user=self.user, name='Spinach')
        Ingredient.objects.create(user=self.user, name='Broccoli')

        response = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
