"""Конфигурация приложения страницы Обо мне."""

from django.apps import AppConfig


class AboutConfig(AppConfig):
    """Настройки приложения страницы Обо мне."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "about"
    verbose_name = "Обо мне"
