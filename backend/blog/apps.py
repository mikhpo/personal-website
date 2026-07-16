"""Конфигурация приложения блога."""

from django.apps import AppConfig


class BlogConfig(AppConfig):  # noqa: D101
    name = "blog"
    verbose_name = "Блог"
    default_auto_field = "django.db.models.AutoField"
