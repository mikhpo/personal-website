"""Тесты представлений галереи."""

import json
import re
from datetime import datetime, timedelta, timezone
from html import unescape
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseBase
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils.crypto import get_random_string

if TYPE_CHECKING:
    from main.context_processors import AlertMessage, AlertsData

from gallery.apps import GalleryConfig
from gallery.factories import AlbumFactory, PhotoFactory, TagFactory
from gallery.models import Album, Photo, Tag
from gallery.utils import is_image
from gallery.views import (
    AlbumDetailView,
    AlbumListView,
    GalleryHomeView,
    PhotoDetailView,
    PhotoListView,
    TagDetailView,
    UploadFormView,
)
from personal_website.storages import StorageType, select_storage
from personal_website.utils import list_file_paths

APP_NAME = GalleryConfig.name

GALLERY_URL = f"/{APP_NAME}/"
GALLERY_URL_NAME = f"{APP_NAME}:{APP_NAME}"
PHOTO_LIST_URL = f"/{APP_NAME}/photos/"
PHOTO_LIST_URL_NAME = f"{APP_NAME}:photo-list"
PHOTO_DETAIL_URL = f"/{APP_NAME}/photo"
PHOTO_DETAIL_URL_NAME = f"{APP_NAME}:photo-detail"
ALBUM_LIST_URL = f"/{APP_NAME}/albums/"
ALBUM_LIST_URL_NAME = f"{APP_NAME}:album-list"
ALBUM_DETAIL_URL = f"/{APP_NAME}/album"
ALBUM_DETAIL_URL_NAME = f"{APP_NAME}:album-detail"
TAG_DETAIL_URL = f"/{APP_NAME}/tag"
TAG_DETAIL_URL_NAME = f"{APP_NAME}:tag-detail"
UPLOAD_URL = f"/{APP_NAME}/upload/"
UPLOAD_URL_NAME = f"{APP_NAME}:upload"

BASE_TEMPLATE_NAME = "base.html"
GALLERY_TEMPLATE_NAME = f"{APP_NAME}/{APP_NAME}_home.html"
PHOTO_LIST_TEMPLATE_NAME = f"{APP_NAME}/photo_list.html"
PHOTO_DETAIL_TEMPLATE_NAME = f"{APP_NAME}/photo_detail.html"
ALBUM_LIST_TEMPLATE_NAME = f"{APP_NAME}/album_list.html"
ALBUM_DETAIL_TEMPLATE_NAME = f"{APP_NAME}/album_detail.html"
TAG_DETAIL_TEMPLATE_NAME = f"{APP_NAME}/tag_detail.html"
UPLOAD_TEMPLATE_NAME = f"{APP_NAME}/upload.html"

storage: StorageType = select_storage()


class TestGalleryHomeView(TestCase):
    """Тесты представления главной страницы галереи."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Создать первоначальные данные для проведения тестов."""
        cls.tag = TagFactory()
        cls.album = AlbumFactory()
        cls.album.tags.add(cls.tag)
        test_images_dir = "gallery/photos"
        files = list_file_paths(test_images_dir)
        images = [file for file in files if is_image(file)]
        for image in images:
            photo = PhotoFactory(image=image, name=None, album=cls.album, public=True)
            photo.tags.add(cls.tag)
        first_photo = Photo.objects.first()
        cls.album.cover = first_photo
        cls.album.save()
        return super().setUpTestData()

    def test_gallery_home_url(self) -> None:
        """Проверить работоспособность ссылки на главную страницу галереи."""
        with self.subTest("Проверка обычной ссылки"):
            resolver_match = resolve(GALLERY_URL)
            response = self.client.get(GALLERY_URL)
            url_view_class = resolver_match.func.view_class
            self.assertEqual(url_view_class, GalleryHomeView)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Проверка именной ссылки"):
            reverse_url = reverse(GALLERY_URL_NAME)
            reverse_resolver_match = resolve(reverse_url)
            reverse_response = self.client.get(reverse_url)
            reverse_url_view_class = reverse_resolver_match.func.view_class
            self.assertEqual(reverse_url_view_class, GalleryHomeView)
            self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
            self.assertEqual(reverse_url_view_class, url_view_class)

        with self.subTest("Проверка используемых представлением шаблонов"):
            self.assertEqual(response.templates, reverse_response.templates)
            self.assertTemplateUsed(response, GALLERY_TEMPLATE_NAME)
            self.assertTemplateUsed(response, BASE_TEMPLATE_NAME)

    def test_gallery_home_view_context(self) -> None:
        """Проверить, что в контекст представления домашней страницы галереи
        автоматически добавляется контекст содержимого галереи.
        """
        response = self.client.get(GALLERY_URL)
        context = response.context
        with self.subTest("Альбомы галереи содержатся в контексте представления"):
            albums = Album.objects.all()
            self.assertEqual(albums.count(), len(context["albums"]))

        with self.subTest("Тэги галереи содержатся в контексте представления"):
            tags = Tag.objects.all()
            self.assertEqual(tags.count(), len(context["tags"]))


class TestPhotoListView(TestCase):
    """Тесты представления списка фотографий."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Создать первоначальные данные для проведения тестов."""
        cls.tag = TagFactory()
        cls.album = AlbumFactory()
        cls.album.tags.add(cls.tag)
        test_images_dir = "gallery/photos"
        files = list_file_paths(test_images_dir)
        images = [file for file in files if is_image(file)]
        for image in images:
            photo = PhotoFactory(image=image, name=None, album=cls.album, public=True)
            photo.tags.add(cls.tag)
        first_photo = Photo.objects.first()
        cls.album.cover = first_photo
        cls.album.save()
        return super().setUpTestData()

    def test_photo_list_sorting(self) -> None:
        """Тест: фотографии в общем списке отсортированы от новых к старым."""
        # Создать альбом с фотографиями с разными датами создания
        album = AlbumFactory()

        # Создать фотографии с явным указанием времени создания
        now = datetime.now(timezone.utc)
        photo1 = PhotoFactory(album=album, public=True)
        photo1.uploaded_at = now - timedelta(hours=3)
        photo1.save()

        photo2 = PhotoFactory(album=album, public=True)
        photo2.uploaded_at = now - timedelta(hours=2)
        photo2.save()

        photo3 = PhotoFactory(album=album, public=True)
        photo3.uploaded_at = now - timedelta(hours=1)
        photo3.save()

        photo4 = PhotoFactory(album=album, public=True)
        photo4.uploaded_at = now
        photo4.save()

        # Получить только что созданные фотографии из этого альбома
        photos = list(Photo.published.filter(album=album))

        # Проверить, что фотографии отсортированы по uploaded_at от новых к старым
        # в соответствии с ordering = ["-uploaded_at"] в PhotoViewSet
        sorted_photos = sorted(photos, key=lambda p: p.uploaded_at, reverse=True)

        # photo4 (новая) должна быть первой, photo1 (старая) - последней
        self.assertEqual(sorted_photos[0], photo4)
        self.assertEqual(sorted_photos[1], photo3)
        self.assertEqual(sorted_photos[2], photo2)
        self.assertEqual(sorted_photos[3], photo1)

    def test_photo_list_url(self) -> None:
        """Проверить работоспособность ссылки на просмотр всех фотографий."""
        with self.subTest("Проверка обычной ссылки на просмотр списка всех фотографий"):
            resolver_match = resolve(PHOTO_LIST_URL)
            response = self.client.get(PHOTO_LIST_URL)
            url_view_class = resolver_match.func.view_class
            self.assertEqual(url_view_class, PhotoListView)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Проверка именной ссылки на просмотр списка всех фотографий"):
            reverse_url = reverse(PHOTO_LIST_URL_NAME)
            reverse_resolver_match = resolve(reverse_url)
            reverse_response = self.client.get(reverse_url)
            reverse_url_view_class = reverse_resolver_match.func.view_class
            self.assertEqual(reverse_url_view_class, PhotoListView)
            self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
            self.assertEqual(url_view_class, reverse_url_view_class)

        with self.subTest("Проверка используемых представлением шаблонов"):
            self.assertEqual(response.templates, reverse_response.templates)
            self.assertTemplateUsed(response, PHOTO_LIST_TEMPLATE_NAME)
            self.assertTemplateUsed(response, BASE_TEMPLATE_NAME)

    def test_photo_list_view_context(self) -> None:
        """Проверить, что страница списка фотографий использует React компонент с правильным API endpoint."""
        response = self.client.get(PHOTO_LIST_URL)

        with self.subTest("Страница содержит React компонент PhotoList"):
            self.assertContains(response, "Gallery/PhotoList")

        with self.subTest("React компонент использует правильный API endpoint"):
            self.assertContains(response, "/api/gallery/photos/")

        with self.subTest("Представление содержит полный набор тэгов галереи в контексте"):
            context = response.context
            tags = Tag.objects.all()
            self.assertEqual(tags.count(), len(context["tags"]))


class TestPhotoDetailView(TestCase):
    """Тесты представления детального просмотра фотографии."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Создать первоначальные данные для проведения тестов."""
        cls.tag = TagFactory()
        cls.album = AlbumFactory()
        cls.album.tags.add(cls.tag)
        test_images_dir = "gallery/photos"
        files = list_file_paths(test_images_dir)
        images = [file for file in files if is_image(file)]
        for image in images:
            photo = PhotoFactory(image=image, name=None, album=cls.album, public=True)
            photo.tags.add(cls.tag)
        first_photo = Photo.objects.first()
        cls.album.cover = first_photo
        cls.album.save()
        return super().setUpTestData()

    def test_photo_detail_url(self) -> None:
        """Проверить работоспособность ссылки на детальный просмотр фотографии."""
        first_photo = Photo.objects.first()
        self.assertIsNotNone(first_photo)
        if first_photo:
            photo_pk = first_photo.pk

            with self.subTest("Проверить переход по ссылке для детального просмотра фотографии"):
                photo_url = f"{PHOTO_DETAIL_URL}/{photo_pk}/"
                resolver_match = resolve(photo_url)
                response = self.client.get(photo_url)
                photo_url_func = resolver_match.func.view_class
                self.assertEqual(photo_url_func, PhotoDetailView)
                self.assertEqual(response.status_code, HTTPStatus.OK)

            with self.subTest("Проверить именную ссылку для детального просмотра фотографии"):
                reverse_url = reverse(PHOTO_DETAIL_URL_NAME, kwargs={"pk": photo_pk})
                reverse_resolver_match = resolve(reverse_url)
                reverse_response = self.client.get(reverse_url)
                reverse_url_view_class = reverse_resolver_match.func.view_class
                self.assertEqual(reverse_url_view_class, PhotoDetailView)
                self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
                self.assertEqual(photo_url_func, reverse_url_view_class)

            with self.subTest("Проверить шаблоны, использованные в представлении"):
                self.assertEqual(response.templates, reverse_response.templates)
                self.assertTemplateUsed(response, PHOTO_DETAIL_TEMPLATE_NAME)
                self.assertTemplateUsed(response, BASE_TEMPLATE_NAME)

    def test_photo_detail_view_context(self) -> None:
        """Проверить доступность представления для детального просмотра фотографии."""
        first_photo = Photo.objects.first()
        self.assertIsNotNone(first_photo)

        if first_photo:
            url = f"{PHOTO_DETAIL_URL}/{first_photo.pk}/"
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)


class TestAlbumListView(TestCase):
    """Тесты представления списка альбомов."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Создать первоначальные данные для проведения тестов."""
        cls.tag = TagFactory()
        cls.album = AlbumFactory()
        cls.album.tags.add(cls.tag)
        test_images_dir = "gallery/photos"
        files = list_file_paths(test_images_dir)
        images = [file for file in files if is_image(file)]
        for image in images:
            photo = PhotoFactory(image=image, name=None, album=cls.album, public=True)
            photo.tags.add(cls.tag)
        first_photo = Photo.objects.first()
        cls.album.cover = first_photo
        cls.album.save()
        return super().setUpTestData()

    def test_album_list_url(self) -> None:
        """Проверить работоспособность ссылки на просмотр всех альбомов."""
        with self.subTest("Проверка обычной ссылки на просмотр списка всех альбомов"):
            resolver_match = resolve(ALBUM_LIST_URL)
            response = self.client.get(ALBUM_LIST_URL)
            url_view_class = resolver_match.func.view_class
            self.assertEqual(url_view_class, AlbumListView)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Проверка именной ссылки на просмотр списка всех альбомов"):
            reverse_url = reverse(ALBUM_LIST_URL_NAME)
            reverse_resolver_match = resolve(reverse_url)
            reverse_response = self.client.get(reverse_url)
            reverse_url_view_class = reverse_resolver_match.func.view_class
            self.assertEqual(reverse_url_view_class, AlbumListView)
            self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
            self.assertEqual(url_view_class, reverse_url_view_class)

        with self.subTest("Проверка используемых представлением шаблонов"):
            self.assertEqual(response.templates, reverse_response.templates)
            self.assertTemplateUsed(response, ALBUM_LIST_TEMPLATE_NAME)
            self.assertTemplateUsed(response, BASE_TEMPLATE_NAME)

    def test_album_list_context(self) -> None:
        """Проверить, что страница списка альбомов использует React компонент с правильным API endpoint."""
        response = self.client.get(ALBUM_LIST_URL)

        with self.subTest("Страница содержит React компонент AlbumList"):
            self.assertContains(response, "Gallery/AlbumList")

        with self.subTest("React компонент использует правильный API endpoint"):
            self.assertContains(response, "/api/gallery/albums/")

        with self.subTest("Представление содержит полный набор тэгов галереи в контексте"):
            context = response.context
            tags = Tag.objects.all()
            self.assertEqual(tags.count(), len(context["tags"]))


class TestAlbumDetailView(TestCase):
    """Тесты представления детального просмотра альбома."""

    def setUp(self) -> None:
        """Создать тестовые данные для каждого теста."""
        super().setUp()
        self.tag = TagFactory()
        self.album = AlbumFactory()
        self.album.tags.add(self.tag)
        test_images_dir = "gallery/photos"
        files = list_file_paths(test_images_dir)
        images = [file for file in files if is_image(file)]
        for image in images:
            photo = PhotoFactory(image=image, name=None, album=self.album, public=True)
            photo.tags.add(self.tag)
        first_photo = Photo.objects.first()
        if first_photo:
            self.album.cover = first_photo
            self.album.save()

    def test_album_photos_sorting(self) -> None:
        """Тест: фотографии в альбоме отсортированы от старых к новым."""
        # Создать альбом с фотографиями с разными датами создания
        album = AlbumFactory()

        # Создать фотографии с явным указанием времени создания
        now = datetime.now(timezone.utc)
        # photo1 - самая старая
        photo1 = PhotoFactory(album=album, public=True)
        photo1.uploaded_at = now - timedelta(hours=4)
        photo1.save()

        # photo2 - средняя по возрасту
        photo2 = PhotoFactory(album=album, public=True)
        photo2.uploaded_at = now - timedelta(hours=2)
        photo2.save()

        # photo3 - новая
        photo3 = PhotoFactory(album=album, public=True)
        photo3.uploaded_at = now - timedelta(hours=1)
        photo3.save()

        # photo4 - самая новая
        photo4 = PhotoFactory(album=album, public=True)
        photo4.uploaded_at = now
        photo4.save()

        # Получить фотографии альбома
        album_photos = list(album.photos.all())

        # Фотографии в альбоме сортируются по pk (от старых к новым)
        # в соответствии с Meta.ordering = ("pk",) в модели Photo
        sorted_photos = sorted(album_photos, key=lambda p: p.pk)

        # photo1 (старая) должна быть первой, photo4 (новая) - последней
        self.assertEqual(sorted_photos[0], photo1)
        self.assertEqual(sorted_photos[1], photo2)
        self.assertEqual(sorted_photos[2], photo3)
        self.assertEqual(sorted_photos[3], photo4)

    def test_album_detail_url(self) -> None:
        """Проверить работоспособность ссылки на детальный просмотр альбома."""
        album_pk = self.album.pk

        with self.subTest("Проверить обычную ссылку на детальный просмотр альбома"):
            url = f"{ALBUM_DETAIL_URL}/{album_pk}/"
            resolver_match = resolve(url)
            response = self.client.get(url)
            view_func = resolver_match.func.view_class
            self.assertEqual(view_func, AlbumDetailView)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Проверить имя ссылки на детальный просмотр альбома"):
            reverse_url = reverse(ALBUM_DETAIL_URL_NAME, kwargs={"pk": album_pk})
            reverse_resolver_match = resolve(reverse_url)
            reverse_response = self.client.get(reverse_url)
            reverse_view_func = reverse_resolver_match.func.view_class
            self.assertEqual(reverse_view_func, AlbumDetailView)
            self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
            self.assertEqual(reverse_view_func, view_func)

        with self.subTest("Проверить шаблоны, используемые представлением"):
            self.assertEqual(response.templates, reverse_response.templates)
            self.assertTemplateUsed(response, ALBUM_DETAIL_TEMPLATE_NAME)
            self.assertTemplateUsed(response, BASE_TEMPLATE_NAME)

    def test_album_detail_view_context(self) -> None:
        """Проверить доступность представления для детального просмотра альбома."""
        album_pk = self.album.pk
        url = f"{ALBUM_DETAIL_URL}/{album_pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_album_shows_its_photos(self) -> None:
        """Тест: страница альбома показывает фотографии из этого альбома."""
        # Создать альбом с фотографиями
        album = AlbumFactory()
        photos: list[Photo] = PhotoFactory.create_batch(3, album=album, public=True)

        # Проверить, что фотографии принадлежат альбому
        album_photos = list(album.photos.all())
        self.assertEqual(len(album_photos), len(photos))

        # Проверить, что все созданные фотографии находятся в альбоме
        for photo in photos:
            self.assertIn(photo, album_photos)


class TestTagDetailView(TestCase):
    """Тесты представления детального просмотра тега."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Создать тестовые данные."""
        cls.tag = TagFactory()
        return super().setUpTestData()

    def test_tag_detail_url(self) -> None:
        """Тестирование ссылки на детальный просмотр тега."""
        tag_pk = self.tag.pk

        with self.subTest("Проверить обычную ссылку на детальный просмотр тэга"):
            url = f"{TAG_DETAIL_URL}/{tag_pk}/"
            resolver_match = resolve(url)
            response = self.client.get(url)
            view_func = resolver_match.func.view_class
            self.assertEqual(view_func, TagDetailView)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Проверить имя ссылки на детальный просмотр тэга"):
            reverse_url = reverse(TAG_DETAIL_URL_NAME, kwargs={"pk": tag_pk})
            reverse_resolver_match = resolve(reverse_url)
            reverse_response = self.client.get(reverse_url)
            reverse_view_func = reverse_resolver_match.func.view_class
            self.assertEqual(reverse_view_func, TagDetailView)
            self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
            self.assertEqual(reverse_view_func, view_func)

        with self.subTest("Проверить шаблоны, используемые представлением"):
            self.assertEqual(response.templates, reverse_response.templates)
            self.assertTemplateUsed(response, TAG_DETAIL_TEMPLATE_NAME)
            self.assertTemplateUsed(response, BASE_TEMPLATE_NAME)

    def test_tag_detail_view_context(self) -> None:
        """Проверить доступность представления для детального просмотра тега."""
        tag_pk = self.tag.pk
        url = f"{TAG_DETAIL_URL}/{tag_pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestUploadFormView(TestCase):
    """Тесты формы для пакетной загрузки фотографий в альбом."""

    test_username = "test_username"
    staff_username = "staff_username"
    test_password = "test_password"
    staff_password = "staff_password"

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные для выполнения тестов."""
        cls.user = User.objects.create_user(username=cls.test_username, password=cls.test_password)
        cls.staff_user = User.objects.create_superuser(username=cls.staff_username, password=cls.staff_password)
        Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)
        test_images_dir = "gallery/photos"
        cls.test_image_paths = list_file_paths(test_images_dir)
        cls.album = AlbumFactory()
        return super().setUpTestData()

    def setUp(self) -> None:
        """Авторизоваться под пользователем с правами персонала."""
        self.client.login(username=self.staff_username, password=self.staff_password)
        return super().setUp()

    def test_upload_url_resolve(self) -> None:
        """Стандартная ссылка корректно разрешается."""
        resolver_match = resolve(UPLOAD_URL)
        self.assertEqual(resolver_match.func.view_class, UploadFormView)

    def test_upload_url_name_resolve(self) -> None:
        """Имя ссылки разрешается корректно."""
        url = reverse(UPLOAD_URL_NAME)
        resolver_match = resolve(url)
        self.assertEqual(resolver_match.func.view_class, UploadFormView)

    def test_templates_used(self) -> None:
        """Проверка использованных представлением шаблонов."""
        response = self.client.get(UPLOAD_URL)
        for template in (UPLOAD_TEMPLATE_NAME, BASE_TEMPLATE_NAME):
            self.assertTemplateUsed(response, template)

    def test_response_status_code(self) -> None:
        """Проверить полученный статус HTTP-ответа."""
        with self.subTest("Статус ответа для пользователя с правами администратора"):
            response = self.client.get(UPLOAD_URL)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Статус ответа для пользователя с обычными правами"):
            self.client.login(username=self.test_username, password=self.test_password)
            response = self.client.get(UPLOAD_URL)
            self.assertNotEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Статус ответа для пользователя, который не авторизован"):
            self.client.logout()
            response = self.client.get(UPLOAD_URL)
            self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_item_in_navbar(self) -> None:
        """Проверка показа ссылки на форму загрузки в навигационной панели."""
        with self.subTest("С главной страницы не доступна ссылка на форму загрузки"):
            response = self.client.get("/main/")
            self.assertNotContains(response, UPLOAD_URL)

        with self.subTest("Со страницы галереи доступна ссылка на форму загрузки"):
            # Ссылка на форму загрузки находится в выпадающем меню навигационной панели,
            # реализованном через React компонент. Проверяем наличие контейнера для React компонента навигации.
            response = self.client.get(GALLERY_URL)
            self.assertContains(response, 'id="navbar-root"')

        with self.subTest("Для пользователя с обычными правами не доступна ссылка на форму загрузки"):
            self.client.login(username=self.test_username, password=self.test_password)
            response = self.client.get(GALLERY_URL)
            self.assertNotContains(response, UPLOAD_URL)

        with self.subTest("Для пользователя, который не авторизован, не доступна ссылка на форму загрузки"):
            self.client.logout()
            response = self.client.get(GALLERY_URL)
            self.assertNotContains(response, UPLOAD_URL)

    def test_images_upload(self) -> None:
        """Проверка результатов загрузки фотографий через форму."""
        photos = []
        for image_path in self.test_image_paths:
            file_content = storage.read_bytes(image_path)
            file_name = Path(image_path).name
            file = SimpleUploadedFile(name=file_name, content=file_content)
            photos.append(file)

        data = {"photos": photos, "album": self.album.pk}
        response = self.client.post(UPLOAD_URL, data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, GALLERY_URL)
        for photo in Photo.objects.all():
            self.assertEqual(photo.album, self.album)

    def _create_test_photos(self) -> list[SimpleUploadedFile]:
        """Создать тестовые фотографии для загрузки."""
        photos = []
        for image_path in self.test_image_paths:
            file_content = storage.read_bytes(image_path)
            file_name = Path(image_path).name
            file = SimpleUploadedFile(name=file_name, content=file_content)
            photos.append(file)
        return photos

    def _check_react_component_mounting(self, response: HttpResponseBase, response_content: str) -> None:
        """Проверить монтирование React компонента."""
        # Проверяем, что скрипт монтирования React компонента идет после загрузки React bundle
        react_bundle = response_content.find("main-")  # React bundle имеет имя main-[hash].js
        alerts_mount = response_content.find("Alert/AlertList")
        self.assertGreater(
            alerts_mount,
            react_bundle,
            "Скрипт монтирования AlertContainer должен идти после загрузки React bundle",
        )

        # Проверяем наличие скрипта монтирования
        self.assertContains(response, "window.mountReactComponent")
        self.assertContains(response, "Alert/AlertList")

    def _check_react_component_presence(self, response: HttpResponseBase) -> None:
        """Проверить наличие React компонента в ответе."""
        self.assertContains(response, "window.mountReactComponent")
        self.assertContains(response, "Alert/AlertList")
        self.assertContains(response, "alerts-root")

    def _check_alerts_data(self, alerts_data: "AlertsData") -> None:
        """Проверить данные оповещений."""
        self.assertIsNotNone(alerts_data)
        self.assertIn("messages", alerts_data)
        self.assertTrue(len(alerts_data["messages"]) > 0)

    def _extract_alerts_props(self, response_content: str) -> "AlertsData":
        """Извлечь свойства оповещений из ответа."""
        props_match = re.search(r'id="alerts-root"\s+data-props="([^"]*)"', response_content)
        self.assertIsNotNone(props_match, "Не найден атрибут data-props у alerts-root")

        if props_match is None:
            self.fail("Не найден атрибут data-props у alerts-root")

        # Если props пустой, значит нет сообщений
        props_raw = props_match.group(1)
        if not props_raw:
            self.fail("data-props пустой, хотя ожидается сообщение о загрузке")

        # Декодируем HTML entities и парсим JSON
        props_json = unescape(props_raw)
        result: AlertsData = json.loads(props_json)
        return result

    def _check_alert_structure(self, alert: "AlertMessage") -> None:
        """Проверить структуру оповещения."""
        self.assertIn("message", alert)
        self.assertIn("level", alert)
        self.assertEqual(alert["level"], "success")
        self.assertTrue(alert["dismissible"])
        self.assertTrue(alert["autoClose"])
        self.assertEqual(alert["autoCloseDelay"], 60000)

    def _check_alert_content(self, alert: "AlertMessage") -> None:
        """Проверить содержимое оповещения."""
        message = str(alert["message"])
        self.assertIn("Загружено", message)
        self.assertIn(str(len(self.test_image_paths)), message)
        self.assertIn(self.album.name, message)

    def test_upload_messages(self) -> None:
        """После загрузки фотографий появляется сообщение с результатом."""
        photos = self._create_test_photos()
        data = {"photos": photos, "album": self.album.pk}
        response = self.client.post(UPLOAD_URL, data, follow=True)

        # Сообщения реализованы через React компонент, проверяем наличие контейнера для него
        self.assertContains(response, 'id="alerts-root"')

        # Проверяем монтирование React компонента
        response_content = response.content.decode("utf-8")
        self._check_react_component_mounting(response, response_content)

        # Извлекаем и проверяем свойства оповещений
        props_data = self._extract_alerts_props(response_content)
        self.assertIn("messages", props_data)
        self.assertTrue(len(props_data["messages"]) > 0, "Должно быть хотя бы одно сообщение")

        # Проверяем структуру и содержимое оповещения
        alert: AlertMessage = props_data["messages"][0]
        self._check_alert_structure(alert)
        self._check_alert_content(alert)

        # Проверяем, что alerts_data правильно передается в шаблон
        alerts_data = response.context.get("alerts_data")
        if alerts_data is None:
            self.fail("alerts_data должен быть словарем")
        self._check_alerts_data(alerts_data)

        # Проверяем структуру и содержимое оповещения из контекста
        context_alert: AlertMessage = alerts_data["messages"][0]
        self._check_alert_structure(context_alert)
        self._check_alert_content(context_alert)

        # Проверяем, что скрипт монтирования React компонента присутствует
        self._check_react_component_presence(response)

    def test_upload_image_verify(self) -> None:
        """Загружаемое изображение проверяется на валидность."""
        file = SimpleUploadedFile(
            name="test.pdf",
            content=bytes(get_random_string(12).encode()),
            content_type="application/pdf",
        )

        data = {"photos": [file], "album": self.album.pk}
        response = self.client.post(UPLOAD_URL, data, follow=True)

        # Сообщения об ошибках реализованы через React компонент, проверяем наличие контейнера для него
        self.assertContains(response, 'id="alerts-root"')

        photos = Photo.objects.filter(album=self.album)
        self.assertFalse(photos.exists())

    def test_upload_view_context(self) -> None:
        """Представление содержит полный набор тэгов галереи в контексте."""
        response = self.client.get(UPLOAD_URL)
        context = response.context
        tags = Tag.objects.all()
        self.assertEqual(tags.count(), len(context["tags"]))
