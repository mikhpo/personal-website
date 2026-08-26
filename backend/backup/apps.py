"""Конфигурация приложения резервного копирования."""

from django.apps import AppConfig


class BackupConfig(AppConfig):  # noqa: D101
    name = "backup"
    default_auto_field = "django.db.models.BigAutoField"
