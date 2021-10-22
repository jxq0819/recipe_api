from core.models import Recipe, Tag, Ingredient
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def create_sample_recipe(user, **params):
    """Create a sample recipe"""
    defaults = {'title': 'Sample recipe', 'time_minutes': 10, 'price': 5.00}
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def create_sample_tag(user, name='Sample tag'):
    """Create a sample tag"""
    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user, name='Sample ingredient'):
    """Create a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def get_recipe_detail_url(recipe_id):
    """Get the recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


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

    def test_recipes_limited_to_user(self):
        """Test listed recipes limited to the authenticated user"""
        user2 = get_user_model().objects.create_user(email='another@test.com', password='TestAnother')
        create_sample_recipe(user=self.user)
        create_sample_recipe(user=user2)

        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_recipe_detail(self):
        """Test retrieving recipe detail"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        recipe.ingredients.add(create_sample_ingredient(user=self.user))

        url = get_recipe_detail_url(recipe.id)
        response = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating a new basic recipe"""
        payload = {'title': 'Chicken sandwich', 'time_minutes': 8, 'price': 5.50}
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a new recipe with tags"""
        tag1 = create_sample_tag(user=self.user, name='Low fat')
        tag2 = create_sample_tag(user=self.user, name='Organic')

        payload = {'title': 'Caesar salad', 'tags': [tag1.id, tag2.id], 'time_minutes': 5, 'price': 7.50}
        response = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_basic_recipe_with_ingredients(self):
        """Test creating a new recipe with ingredients"""
        ingredient1 = create_sample_ingredient(user=self.user, name='Butter')
        ingredient2 = create_sample_ingredient(user=self.user, name='Mussel')

        payload = {'title': 'Garlic butter mussels',
                   'ingredients': [ingredient1.id, ingredient2.id],
                   'time_minutes': 5,
                   'price': 7.50}
        response = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
