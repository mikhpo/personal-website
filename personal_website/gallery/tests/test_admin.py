import os
import shutil
from http import HTTPStatus
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from gallery.apps import GalleryConfig
from gallery.models import Album, Photo, Tag
from personal_website.utils import list_image_paths

ADMIN_URL = "/admin/"


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, "temp"))
class GalleryAdminTest(TestCase):
    """
    Тестирование функциональности раздела галереи в административном интерфейсе Django.
    """

    @classmethod
    def setUpTestData(cls):
        cls.superuser: User = User.objects.create_superuser(
            username="testadmin", password="12345"
        )

    def setUp(self):
        os.makedirs(settings.MEDIA_ROOT)
        self.client.login(username="testadmin", password="12345")

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_gallery_admin_page_displayed(self):
        """
        Проверяет, что в административной панели отображется раздел галереи.
        """
        app_verbose_name = GalleryConfig.verbose_name
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, app_verbose_name)
        response = self.client.get(ADMIN_URL + "gallery/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for action in ["Добавить", "Изменить"]:
            self.assertContains(response, action)

    def test_photo_admin_page_displayed(self):
        """
        Проверяет, что в административной панели отображается модель фотографии.
        """
        photos_verbose_name = Photo._meta.verbose_name_plural
        self.assertNotEqual(photos_verbose_name, None)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, photos_verbose_name)
        response = self.client.get(ADMIN_URL + "gallery/photo/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_album_admin_page_displayed(self):
        """
        Проверяет, что в административной панели отображается модель альбома.
        """
        albums_verbose_name = Album._meta.verbose_name_plural
        self.assertNotEqual(albums_verbose_name, None)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, albums_verbose_name)
        response = self.client.get(ADMIN_URL + "gallery/album/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tag_admin_page_displayed(self):
        """
        Проверяет, что в административной панели отображается модель тэга.
        """
        tags_verbose_name = Tag._meta.verbose_name_plural
        self.assertNotEqual(tags_verbose_name, None)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, tags_verbose_name)
        response = self.client.get(ADMIN_URL + "gallery/tag/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_photo_add_via_admin(self):
        """
        Проверяет успешность добавления фотографии через административную панель.
        """
        # Создать альбом, в который будет добавляться фотография.
        album = Album.objects.create(name="Тестовый альбом")

        # Ссылка на форму добавления фотографии в административной панели.
        photo_add_url = ADMIN_URL + "gallery/photo/add/"
        response = self.client.get(photo_add_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Получение фотографии, которая будет загружена.
        image_path = list_image_paths()[0]
        photo_image = open(image_path, "rb")
        photo_name = Path(image_path).stem

        # Загрузить фотографию, проверить статус ответа и что фотография с именем исходного файла существует в базе данных.
        response = self.client.post(
            photo_add_url,
            data={
                "image": SimpleUploadedFile(photo_image.name, photo_image.read()),
                "album": album.pk,
                "public": True,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Photo.objects.filter(name=photo_name).exists())

    def test_tag_add_via_admin(self):
        """
        Проверяет, что тэги можно успешно добавлять через административную панель.
        """
        _TEST_TAG_NAME = "test"

        # Ссылка на форму добавления тэга в административной панели.
        tag_add_url = ADMIN_URL + "gallery/tag/add/"
        response = self.client.get(tag_add_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Заполнить форму, отправить форму, проверить статус ответа.
        response = self.client.post(tag_add_url, data={"name": _TEST_TAG_NAME})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Проверить, что тэг с указанным именем существует в базе данных и что слаг автоматически создан.
        queryset = Tag.objects.filter(name=_TEST_TAG_NAME)
        self.assertTrue(queryset.exists())
        tag = queryset.first()
        self.assertEqual(tag.slug, "test")

    def test_album_add_via_admin(self):
        """
        Проверяет, что альбомы можно успешно добавлять через административную панель.
        """
        _TEST_ALBUM_NAME = "Test album"

        # Ссылка на форму добавления альбома в административной панели.
        album_add_url = ADMIN_URL + "gallery/album/add/"
        response = self.client.get(album_add_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Заполнить форму, отправить форму, проверить статус ответа.
        response = self.client.post(
            album_add_url, data={"name": _TEST_ALBUM_NAME, "public": True}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Проверить, что альбом с указанным именем существует в базе данных и что слаг автоматически создан.
        queryset = Album.objects.filter(name=_TEST_ALBUM_NAME)
        self.assertTrue(queryset.exists())
        album = queryset.first()
        self.assertEqual(album.slug, "test-album")
