"""Сериализаторы главного раздела сайта."""

from rest_framework import serializers

from main.models import AboutPage


class AboutPageSerializer(serializers.ModelSerializer):
    """Сериализатор страницы Обо мне."""

    class Meta:  # noqa: D106
        model = AboutPage
        fields = ("content",)
