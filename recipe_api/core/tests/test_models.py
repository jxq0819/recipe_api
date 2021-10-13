from django.contrib.auth import get_user_model
from django.test import TestCase

from .. import models


def create_sample_user():
    email = 'sample@test.com'
    password = 'SAMPLE_password'
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):

    def test_create_user_with_email_address(self):
        """Test creating a new user with an email is successful"""
        email = 'test@test.com'
        password = 'TestPassword12'
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        """Test the email for a new user is normalised"""
        email = 'test@TEST.COM'
        password = '12testPassword'
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating a new user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None, password='TESTPassword!')

    def test_create_superuser(self):
        """Test creating a new superuser"""
        email = 'admin@admin.com'
        password = 'AdminPassword'
        user = get_user_model().objects.create_superuser(email=email, password=password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_string(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(user=create_sample_user(), name='Veganism')

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_string(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(user=create_sample_user(), name='Tomato')

        self.assertEqual(str(ingredient), ingredient.name)
