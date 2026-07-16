"""Модуль для построения карты сайта по объектам галереи."""

from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.db.models import QuerySet

from gallery.models import Album, Photo, Tag

PROTOCOL = "https"


class TagSitemap(Sitemap):
    """Карта сайта для тэгов."""

    protocol = PROTOCOL

    def items(self) -> QuerySet[Tag]:
        """Все тэги."""
        return Tag.objects.all()


class AlbumSitemap(Sitemap):
    """Карта сайта для альбомов."""

    protocol = PROTOCOL

    def items(self) -> QuerySet[Album]:
        """Все публичные альбомы."""
        return Album.published.all()

    def lastmod(self, obj: Album) -> datetime:
        """Время последнего изменения альбома."""
        return obj.updated_at


class PhotoSitemap(Sitemap):
    """Карта сайта для фотографий."""

    protocol = PROTOCOL

    def items(self) -> QuerySet[Photo]:
        """Все публичные фотографии."""
        return Photo.published.all()

    def lastmod(self, obj: Photo) -> datetime:
        """Время последнего изменения фотографии."""
        return obj.modified_at
