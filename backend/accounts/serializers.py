"""Сериализаторы для приложения accounts."""

from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:  # noqa: D106
        model = User
        fields = ("id", "username", "password")

    def create(self, validated_data: dict) -> User:
        """Создать пользователя с хешированным паролем.

        Пароль хешируется до единственного сохранения: в базу данных
        и в журнал аудита не должен попадать пароль в открытом виде.
        """
        raw_password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(raw_password)
        user.save()
        return user

    def update(self, instance: User, validated_data: dict) -> User:
        """Обновить пользователя, хешируя пароль при его смене."""
        raw_password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)
        if raw_password:
            instance.set_password(raw_password)
            instance.save(update_fields=["password"])
        return instance
