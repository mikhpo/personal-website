"""Сериализаторы приложения страницы Обо мне."""

from rest_framework import serializers

from about.models import AboutPage


class AboutPageSerializer(serializers.ModelSerializer):
    """Сериализатор страницы Обо мне."""

    class Meta:  # noqa: D106
        model = AboutPage
        fields = ("content",)
