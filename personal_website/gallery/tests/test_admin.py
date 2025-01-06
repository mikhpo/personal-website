"""Тесты представлений галереи в административной панели Django."""

import os
from http import HTTPStatus
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from gallery.apps import GalleryConfig
from gallery.factories import AlbumFactory, PhotoFactory
from gallery.models import Album, Photo, Tag
from personal_website.utils import list_file_paths

ADMIN_URL = "/admin/"


class GalleryAdminTests(TestCase):
    """Тестирование функциональности раздела галереи в административном интерфейсе Django."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные для выполнения тестов."""
        cls.superuser: User = User.objects.create_superuser(username="testadmin", password="12345")
        temp_dir = os.getenv("TEMP_ROOT", default=settings.PROJECT_DIR / "temp")
        test_images_dir = Path(temp_dir) / "gallery" / "photos"
        cls.image_path = list_file_paths(test_images_dir)[0]
        return super().setUpTestData()

    def setUp(self) -> None:
        """Авторизоваться под пользователем-администратором."""
        self.client.login(username="testadmin", password="12345")
        return super().setUp()

    def test_gallery_admin_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображется раздел галереи."""
        app_verbose_name = GalleryConfig.verbose_name
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, app_verbose_name)
        url = ADMIN_URL + "gallery/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for action in ["Добавить", "Изменить"]:
            self.assertContains(response, action)

    def test_photo_admin_list_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображается модель фотографии."""
        url = ADMIN_URL + "gallery/photo/"
        photos_verbose_name = Photo._meta.verbose_name_plural  # noqa: SLF001
        self.assertIsNotNone(photos_verbose_name)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, str(photos_verbose_name))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_photo_change_page_rendered(self) -> None:
        """Проверяет корректность отображения страницы изменения фотографии."""
        with self.subTest("Получение страницы детального просмотра и изменения"):
            album = AlbumFactory(name="Test album")
            photo = PhotoFactory(name="Test photo", album=album, image=None)
            slug = "test-photo"
            url = ADMIN_URL + f"gallery/photo/{photo.pk}/change/"
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(photo.slug, slug)
            self.assertIsNone(photo.image.name)

        with self.subTest("Отправка данных для изменения объекта"):
            new_slug = "new-slug"
            with Path(self.image_path).open("rb") as photo_image:
                data = {
                    "image": SimpleUploadedFile(photo_image.name, photo_image.read()),
                    "name": photo.name,
                    "album": album.pk,
                    "slug": new_slug,
                }
                response = self.client.post(url, data)
            photo.refresh_from_db()
            self.assertEqual(photo.slug, new_slug)
            self.assertIsNotNone(photo.image.name)

    def test_album_admin_list_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображается модель альбома."""
        albums_verbose_name = Album._meta.verbose_name_plural  # noqa: SLF001
        self.assertIsNotNone(albums_verbose_name)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, str(albums_verbose_name))
        url = ADMIN_URL + "gallery/album/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tag_admin_list_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображается модель тэга."""
        tags_verbose_name = Tag._meta.verbose_name_plural  # noqa: SLF001
        self.assertIsNotNone(tags_verbose_name)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, str(tags_verbose_name))
        url = ADMIN_URL + "gallery/tag/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_photo_add_via_admin(self) -> None:
        """Проверяет успешность добавления фотографии через административную панель."""
        # Создать альбом, в который будет добавляться фотография.
        album = AlbumFactory(name="Тестовый альбом")
        photo_name = Path(self.image_path).stem

        # Ссылка на форму добавления фотографии в административной панели.
        url = ADMIN_URL + "gallery/photo/add/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Загрузить фотографию, проверить статус ответа и что
        # фотография с именем исходного файла существует в базе данных.
        with Path(self.image_path).open("rb") as photo_image:
            data = {
                "image": SimpleUploadedFile(photo_image.name, photo_image.read()),
                "album": album.pk,
                "public": True,
            }
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Photo.objects.filter(name=photo_name).exists())

    def test_tag_add_via_admin(self) -> None:
        """Проверяет, что тэги можно успешно добавлять через административную панель."""
        test_tag_name = "test"

        # Ссылка на форму добавления тэга в административной панели.
        url = ADMIN_URL + "gallery/tag/add/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Заполнить форму, отправить форму, проверить статус ответа.
        response = self.client.post(url, data={"name": test_tag_name})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Проверить, что тэг с указанным именем существует в базе данных и что слаг автоматически создан.
        queryset = Tag.objects.filter(name=test_tag_name)
        self.assertTrue(queryset.exists())
        tag = queryset.first()
        self.assertIsNotNone(tag)
        if tag:
            self.assertEqual(tag.slug, "test")

    def test_album_add_via_admin(self) -> None:
        """Проверяет, что альбомы можно успешно добавлять через административную панель."""
        test_album_name = "Test album"

        # Ссылка на форму добавления альбома в административной панели.
        url = ADMIN_URL + "gallery/album/add/"

        # Заполнить форму, отправить форму, проверить статус ответа.
        data = {
            "name": test_album_name,
            "photo_set-TOTAL_FORMS": 0,
            "photo_set-INITIAL_FORMS": 0,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Проверить, что альбом с указанным именем существует в базе данных и что слаг автоматически создан.
        albums = Album.objects.all()
        album = albums.first()
        self.assertTrue(albums.exists())
        if album:
            self.assertEqual(album.name, test_album_name)
            self.assertEqual(album.slug, "test-album")

    def test_album_admin_change(self) -> None:
        """Проверка представления для изменения альбома."""
        with self.subTest("Получение страницы GET-методом"):
            album = AlbumFactory(name="Test album")
            url = ADMIN_URL + f"gallery/album/{album.pk}/change/"
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Изменение альбома POST-методом"):
            new_slug = "new-slug"
            data = {
                "name": album.name,
                "slug": new_slug,
                "photo_set-TOTAL_FORMS": 0,
                "photo_set-INITIAL_FORMS": 0,
            }
            response = self.client.post(url, data)
            album.refresh_from_db()
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertEqual(album.slug, new_slug)
