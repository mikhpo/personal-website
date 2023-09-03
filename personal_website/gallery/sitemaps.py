"""
Модуль для построения карты сайта по объектам блога.
"""
from django.contrib.sitemaps import Sitemap
from gallery.models import Album, Photo, Tag


class TagSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Tag.objects.all()


class AlbumSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Album.objects.filter(public=True)

    def lastmod(self, obj: Album):
        return obj.updated


class PhotoSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Photo.objects.filter(public=True)

    def lastmod(self, obj: Photo):
        return obj.modified
