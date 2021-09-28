from rest_framework import generics

from .serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """API view of creating a new user"""
    serializer_class = UserSerializer
