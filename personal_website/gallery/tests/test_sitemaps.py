"""Тесты карты сайта для объектов галереи."""

import os
from http import HTTPStatus
from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from gallery.factories import AlbumFactory, PhotoFactory, TagFactory
from gallery.models import Photo, Tag
from personal_website.utils import list_file_paths

SITEMAP_URL = "/sitemap.xml"
TEMP_ROOT = os.getenv("TEMP_ROOT", default=settings.PROJECT_DIR / "temp")


class GallerySitemapTest(TestCase):
    """Тестирование карты галереи."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Метод применяется один раз перед выполнением тестов класса."""
        # Создать теги.
        for tag in ["Путешествия", "Италия", "Тоскана", "Непал", "Лангтанг"]:
            TagFactory(name=tag)

        # Создать альбомы.
        cls.public_album = AlbumFactory(public=True)
        cls.private_album = AlbumFactory(public=False)

        # Создать фотографии в базе данных из картинок в директории проекта.
        test_images_dir = Path(TEMP_ROOT) / "gallery" / "photos"
        images = list_file_paths(test_images_dir)
        for image in images:
            if "Tuscany" in image:
                PhotoFactory(image=image, name=None, public=True, album=cls.public_album)
            else:
                PhotoFactory(image=image, name=None, public=False, album=cls.private_album)

    def test_tag_sitemap(self) -> None:
        """Проверить, что все тэги добавляются в карту сайта."""
        tags = Tag.objects.all()
        response = self.client.get(SITEMAP_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        for tag in tags:
            self.assertTrue(tag.get_absolute_url() in content)

    def test_album_sitemap(self) -> None:
        """Проверить, что альбомы присутствуют в карте сайта, но только публичные."""
        response = self.client.get(SITEMAP_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        local_time = timezone.localtime(self.public_album.updated_at)
        modified_at_date = str(local_time.date())
        self.assertTrue(self.public_album.get_absolute_url() in content)
        self.assertFalse(self.private_album.get_absolute_url() in content)
        self.assertTrue(modified_at_date in content)

    def test_photo_sitemap(self) -> None:
        """Проверить, что фотографии присутствуют в карте сайта, но только публичные."""
        public_photos = Photo.objects.filter(public=True)
        private_photos = Photo.objects.filter(public=False)
        response = self.client.get(SITEMAP_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        for photo in public_photos:
            self.assertTrue(photo.get_absolute_url() in content)
        for photo in private_photos:
            self.assertFalse(photo.get_absolute_url() in content)
