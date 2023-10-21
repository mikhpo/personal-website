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
class GalleryAdminTests(TestCase):
    """
    Тестирование функциональности раздела галереи в административном интерфейсе Django.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.superuser: User = User.objects.create_superuser(
            username="testadmin", password="12345"
        )
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        cls.image_path = list_image_paths()[0]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.photo_image = open(self.image_path, "rb")
        self.photo_name = Path(self.image_path).stem
        self.client.login(username="testadmin", password="12345")

    def test_gallery_admin_page_displayed(self):
        """
        Проверяет, что в административной панели отображется раздел галереи.
        """
        app_verbose_name = GalleryConfig.verbose_name
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, app_verbose_name)
        url = ADMIN_URL + "gallery/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for action in ["Добавить", "Изменить"]:
            self.assertContains(response, action)

    def test_photo_admin_list_page_displayed(self):
        """
        Проверяет, что в административной панели отображается модель фотографии.
        """
        url = ADMIN_URL + "gallery/photo/"
        photos_verbose_name = Photo._meta.verbose_name_plural
        self.assertNotEqual(photos_verbose_name, None)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, photos_verbose_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_photo_change_page_rendered(self):
        """
        Проверяет корректность отображения страницы изменения фотографии.
        """
        with self.subTest("Получение страницы детального просмотра и изменения"):
            album = Album.objects.create(name="Test album")
            photo = Photo.objects.create(name="Test photo", album=album)
            slug = "test-photo"
            url = ADMIN_URL + f"gallery/photo/{photo.pk}/change/"
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(photo.slug, slug)

        with self.subTest("Отправка данных для изменения объекта"):
            new_slug = "new-slug"
            data = {
                "image": SimpleUploadedFile(
                    self.photo_image.name, self.photo_image.read()
                ),
                "name": photo.name,
                "album": album.pk,
                "slug": new_slug,
            }
            response = self.client.post(url, data)
            photo.refresh_from_db()
            self.assertEqual(photo.slug, new_slug)

    def test_album_admin_list_page_displayed(self):
        """
        Проверяет, что в административной панели отображается модель альбома.
        """
        albums_verbose_name = Album._meta.verbose_name_plural
        self.assertNotEqual(albums_verbose_name, None)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, albums_verbose_name)
        url = ADMIN_URL + "gallery/album/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tag_admin_list_page_displayed(self):
        """
        Проверяет, что в административной панели отображается модель тэга.
        """
        tags_verbose_name = Tag._meta.verbose_name_plural
        self.assertNotEqual(tags_verbose_name, None)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, tags_verbose_name)
        url = ADMIN_URL + "gallery/tag/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_photo_add_via_admin(self):
        """
        Проверяет успешность добавления фотографии через административную панель.
        """
        # Создать альбом, в который будет добавляться фотография.
        album = Album.objects.create(name="Тестовый альбом")

        # Ссылка на форму добавления фотографии в административной панели.
        url = ADMIN_URL + "gallery/photo/add/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Загрузить фотографию, проверить статус ответа и что фотография с именем исходного файла существует в базе данных.
        data = {
            "image": SimpleUploadedFile(self.photo_image.name, self.photo_image.read()),
            "album": album.pk,
            "public": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Photo.objects.filter(name=self.photo_name).exists())

    def test_tag_add_via_admin(self):
        """
        Проверяет, что тэги можно успешно добавлять через административную панель.
        """
        _TEST_TAG_NAME = "test"

        # Ссылка на форму добавления тэга в административной панели.
        url = ADMIN_URL + "gallery/tag/add/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Заполнить форму, отправить форму, проверить статус ответа.
        response = self.client.post(url, data={"name": _TEST_TAG_NAME})
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
        url = ADMIN_URL + "gallery/album/add/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Заполнить форму, отправить форму, проверить статус ответа.
        data = {
            "name": _TEST_ALBUM_NAME,
            "photo_set-TOTAL_FORMS": 0,
            "photo_set-INITIAL_FORMS": 0,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Проверить, что альбом с указанным именем существует в базе данных и что слаг автоматически создан.
        queryset = Album.objects.all()
        self.assertTrue(queryset.exists())
        album = queryset.first()
        self.assertEqual(album.name, _TEST_ALBUM_NAME)
        self.assertEqual(album.slug, "test-album")

    def test_album_admin_change(self):
        """
        Проверка представления для изменения альбома.
        """
        with self.subTest("Получение страницы GET-методом"):
            album = Album.objects.create(name="Test album")
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
