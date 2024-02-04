"""Менеджеры галереи."""
from personal_website.managers import PublicManager


class PublicPhotoManager(PublicManager):
    """Менеджер для работы с публичными фотографиями."""


class PublicAlbumManager(PublicManager):
    """Менеджер для работы с публичными альбомами."""
