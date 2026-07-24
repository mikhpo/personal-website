"""Менеджеры галереи."""

from django.db.models.query import QuerySet

from personal_website.managers import PublicManager


class PublicPhotoManager(PublicManager):
    """Менеджер для работы с публичными фотографиями."""


class PublicAlbumManager(PublicManager):
    """Менеджер для работы с публичными альбомами."""


class ChronologicalPhotoManager(PublicManager):
    """Менеджер для фотографий в хронологическом порядке (от старых к новым)."""

    def get_queryset(self) -> QuerySet:
        """Возвращает фотографии, упорядоченные по дате съемки по возрастанию."""
        return super().get_queryset().order_by("taken_at")
