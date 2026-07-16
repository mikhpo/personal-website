"""Сериализаторы для приложения accounts."""

from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        """Мета-класс для определения параметров сериализатора."""

        model = User
        fields = ("id", "username", "password")
