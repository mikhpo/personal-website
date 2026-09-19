"""Сериализаторы приложения страницы Обо мне."""

from rest_framework import serializers

from about.models import About


class AboutSerializer(serializers.ModelSerializer):
    """Сериализатор страницы Обо мне."""

    class Meta:  # noqa: D106
        model = About
        fields = ("content",)
