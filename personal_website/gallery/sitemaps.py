"""
Модуль для построения карты сайта по объектам блога.
"""
from django.contrib.sitemaps import Sitemap

from .models import Album, Photo, Tag


class TagSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Tag.objects.all()


class AlbumSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Album.published.all()

    def lastmod(self, obj: Album):
        return obj.updated_at


class PhotoSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Photo.published.all()

    def lastmod(self, obj: Photo):
        return obj.modified_at
