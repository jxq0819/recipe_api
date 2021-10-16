from core.models import Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

RECIPES_URL = reverse('recipe:recipe-list')


def create_sample_recipe(user, **params):
    """Create a sample recipe"""
    defaults = {'title': 'Sample recipe', 'time_minutes': 10, 'price': 5.00}
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipesTest(TestCase):
    """Test public recipes APIs"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required for listing recipes"""
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesTest(TestCase):
    """Test private recipes APIs"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='test@test.com', password='TestRecipe')
        self.client.force_authenticate(self.user)

    def test_list_recipes(self):
        """Test listing recipes"""
        Recipe.objects.create(user=self.user, title='Sample recipe', time_minutes=10, price=5.00)
        Recipe.objects.create(user=self.user, title='Sample recipe', time_minutes=10, price=5.00)

        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
