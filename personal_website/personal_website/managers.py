"""Менеджеры для управления объектами в базе данных."""

from django.db import models
from django.db.models.query import QuerySet


class PublicManager(models.Manager):
    """Менеджер для работы только с публичными объектами."""

    def get_queryset(self) -> QuerySet:  # noqa: D102
        return super().get_queryset().filter(public=True)
