"""Конфигурация приложения галереи."""
from django.apps import AppConfig


class GalleryConfig(AppConfig):  # noqa: D101
    name = "gallery"
    verbose_name = "Галерея"
    default_auto_field = "django.db.models.BigAutoField"
