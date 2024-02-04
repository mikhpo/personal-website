"""Тесты представлений галереи."""
import os
import random
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils.crypto import get_random_string

from gallery.apps import GalleryConfig
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
from personal_website.utils import list_file_paths

if TYPE_CHECKING:
    from django.db.models import QuerySet

APP_NAME = GalleryConfig.name

GALLERY_URL = f"/{APP_NAME}/"
GALLERY_URL_NAME = f"{APP_NAME}:{APP_NAME}"
PHOTO_LIST_URL = f"/{APP_NAME}/photos/"
PHOTO_LIST_URL_NAME = f"{APP_NAME}:photo-list"
PHOTO_DETAIL_URL = f"/{APP_NAME}/photos"
PHOTO_DETAIL_URL_NAME = f"{APP_NAME}:photo-detail"
ALBUM_DETAIL_URL = f"/{APP_NAME}/albums"
ALBUM_DETAIL_URL_NAME = f"{APP_NAME}:album-detail"
ALBUM_LIST_URL = f"/{APP_NAME}/albums/"
ALBUM_LIST_URL_NAME = f"{APP_NAME}:album-list"
TAG_DETAIL_URL = f"/{APP_NAME}/tags"
TAG_DETAIL_URL_NAME = f"{APP_NAME}:tag-detail"
UPLOAD_URL = f"/{APP_NAME}/upload/"
UPLOAD_URL_NAME = f"{APP_NAME}:upload"

BASE_TEMPLATE_NAME = "base.html"
GALLERY_TEMPLATE_NAME = f"{APP_NAME}/{APP_NAME}_home.html"
PHOTO_LIST_TEMPLATE_NAME = f"{APP_NAME}/photo_list.html"
PHOTO_DETAIL_TEMPLATE_NAME = f"{APP_NAME}/photo_detail.html"
ALBUM_DETAIL_TEMPLATE_NAME = f"{APP_NAME}/album_detail.html"
ALBUM_LIST_TEMPLATE_NAME = f"{APP_NAME}/album_list.html"
TAG_DETAIL_TEMPLATE_NAME = f"{APP_NAME}/tag_detail.html"
TAG_LIST_TEMPLATE_NAME = f"{APP_NAME}/tag_list.html"
UPLOAD_TEMPLATE_NAME = f"{APP_NAME}/upload.html"


class GalleryViewsTest(TestCase):
    """Тестирование представлений галереи."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Создать первоначальные данные для проведения тестов."""
        cls.tag = Tag.objects.create(name="Test tag")
        cls.album = Album.objects.create(name="Test album")
        cls.album.tags.add(cls.tag)
        test_dir = os.getenv("TEMP_ROOT")
        test_images_dir = Path(test_dir) / "gallery" / "photos"
        files = list_file_paths(test_images_dir)
        images = [file for file in files if is_image(file)]
        for image in images:
            photo = Photo.objects.create(image=image, album=cls.album)
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
            for album in albums:
                self.assertContains(response, album)
            self.assertEqual(albums.count(), len(context["albums"]))

        with self.subTest("Тэги галереи содержатся в контексте представления"):
            tags = Tag.objects.all()
            for tag in tags:
                self.assertContains(response, tag)
            self.assertEqual(tags.count(), len(context["tags"]))

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
        """Проверить, что в контекст списка всех фотографий автоматически добавляется набор тэгов."""
        response = self.client.get(PHOTO_LIST_URL)
        context = response.context
        tags = Tag.objects.all()
        for tag in tags:
            self.assertContains(response, tag)
        self.assertEqual(tags.count(), len(context["tags"]))

    def test_photo_detail_url(self) -> None:
        """Проверить работоспособность ссылки на детальный просмотр фотографии."""
        first_photo = Photo.objects.first()
        photo_slug = first_photo.slug

        with self.subTest("Проверить переход по ссылке для детального просмотра фотографии"):
            photo_url = f"{PHOTO_DETAIL_URL}/{photo_slug}/"
            resolver_match = resolve(photo_url)
            response = self.client.get(photo_url)
            photo_url_func = resolver_match.func.view_class
            self.assertEqual(photo_url_func, PhotoDetailView)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Проверить именную ссылку для детального просмотра фотографии"):
            reverse_url = reverse(PHOTO_DETAIL_URL_NAME, args=(photo_slug,))
            reverse_resolver_match = resolve(reverse_url)
            reverse_response = self.client.get(reverse_url)
            photo_url_name_func = reverse_resolver_match.func.view_class
            self.assertEqual(photo_url_name_func, PhotoDetailView)
            self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
            self.assertEqual(photo_url_func, photo_url_name_func)

        with self.subTest("Проверить шаблоны, использованные в представлении"):
            self.assertEqual(response.templates, reverse_response.templates)
            self.assertTemplateUsed(response, PHOTO_DETAIL_TEMPLATE_NAME)
            self.assertTemplateUsed(response, BASE_TEMPLATE_NAME)

    def test_photo_detail_view_context(self) -> None:
        """Проверить содержание представления для детального просмотра фотографии."""
        all_photos = Photo.objects.all()
        sorted_photos = sorted(all_photos, key=lambda photo: photo.datetime_taken)
        first_photo = sorted_photos[0]
        last_photo = sorted_photos[-1]
        middle_photos = all_photos.exclude(pk__in=[first_photo.pk, last_photo.pk])
        middle_photo = random.choice(middle_photos)

        # Создать новый альбом и фотографию в нем.
        new_album = Album.objects.create(name="New test album")
        new_photo = Photo.objects.create(name="New photo", album=new_album)

        # Идентификаторы элементов, соответствующих ссылкам на следующую и предыдущую фотографию.
        next_photo_link_id = "next-photo-link"
        previous_photo_link_id = "previous-photo-link"

        with self.subTest("Для первой фотографии в альбоме доступа только ссылка на следующую фотографию"):
            url = f"{PHOTO_DETAIL_URL}/{first_photo.slug}/"
            response = self.client.get(url)
            context = response.context
            self.assertIsNotNone(context["next_photo"])
            self.assertContains(response, next_photo_link_id)
            self.assertIsNone(context["previous_photo"])
            self.assertNotContains(response, previous_photo_link_id)

        with self.subTest("Для последней фотографии в альбоме доступна только ссылка на предыдущую фотографию"):
            url = f"{PHOTO_DETAIL_URL}/{last_photo.slug}/"
            response = self.client.get(url)
            context = response.context
            self.assertIsNotNone(context["previous_photo"])
            self.assertContains(response, previous_photo_link_id)
            self.assertIsNone(context["next_photo"])
            self.assertNotContains(response, next_photo_link_id)
            self.assertNotContains(response, new_photo.get_absolute_url())

        with self.subTest(
            "Для фотографии в середине альбома доступны и ссылка на "
            "следующую фотографию, и ссылка на предыдущую фотографию",
        ):
            url = f"{PHOTO_DETAIL_URL}/{middle_photo.slug}/"
            response = self.client.get(url)
            context = response.context
            self.assertIsNotNone(context["next_photo"])
            self.assertContains(response, next_photo_link_id)
            self.assertIsNotNone(context["previous_photo"])
            self.assertContains(response, previous_photo_link_id)

        with self.subTest("Представление содержит список тэгов данной фотографии"):
            url = f"{PHOTO_DETAIL_URL}/{first_photo.slug}/"
            response = self.client.get(url)
            context = response.context
            tags = Tag.objects.all()
            for tag in tags:
                self.assertContains(response, tag)
            self.assertEqual(tags.count(), len(context["tags"]))

    def test_album_detail_url(self) -> None:
        """Проверить работоспособность ссылки на детальный просмотр альбома."""
        album_slug = self.album.slug

        with self.subTest("Проверить обычную ссылку на детальный просмотр альбома"):
            url = f"{ALBUM_DETAIL_URL}/{album_slug}/"
            resolver_match = resolve(url)
            response = self.client.get(url)
            view_func = resolver_match.func.view_class
            self.assertEqual(view_func, AlbumDetailView)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Проверить имя ссылки на детальный просмотр альбома"):
            reverse_url = reverse(ALBUM_DETAIL_URL_NAME, kwargs={"slug": album_slug})
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
        """
        Проверить контекст ответа, полученного при запросе страницы детального просмотра альбома.

        В альбоме должны отображаться только публичные фотографии.
        """
        album_slug = self.album.slug
        url = f"{ALBUM_DETAIL_URL}/{album_slug}/"
        all_photos: QuerySet[Photo] = self.album.photo_set.all()
        private_photo = all_photos.last()
        private_photo.public = False
        private_photo.save()
        public_photos = Photo.objects.filter(album=self.album, public=True)
        response = self.client.get(url)
        context = response.context

        with self.subTest("Представление содержит только публичные фотографии"):
            context_photos: QuerySet[Photo] = context["photos"]
            for photo in public_photos:
                self.assertContains(response, photo)
            self.assertNotContains(response, private_photo)
            self.assertEqual(len(context_photos), public_photos.count())

        with self.subTest("Представление содержит список тэгов данного альбома"):
            tags = Tag.objects.all()
            for tag in tags:
                self.assertContains(response, tag)
            self.assertEqual(tags.count(), len(context["tags"]))

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
        """В списке альбомов должны отображаться только публичные альбомы."""
        with self.subTest("Приватный альбом не отображается"):
            self.album.public = False
            self.album.save()
            response = self.client.get(ALBUM_LIST_URL)
            self.assertNotContains(response, self.album)

        with self.subTest("Публичный альбом отображается"):
            self.album.public = True
            self.album.save()
            self.assertTrue(self.album.public)
            response = self.client.get(ALBUM_LIST_URL)
            self.assertContains(response, self.album)

        with self.subTest("Альбом без обложки не отображается"):
            self.album.cover = None
            self.album.save()
            response = self.client.get(ALBUM_LIST_URL)
            self.assertNotContains(response, self.album)

        with self.subTest("Представление содержит полный набор тэгов галереи"):
            context = response.context
            tags = Tag.objects.all()
            for tag in tags:
                self.assertContains(response, tag)
            self.assertEqual(tags.count(), len(context["tags"]))

    def test_tag_detail_url(self) -> None:
        """Тестирование ссылки на детальный просмотр тега."""
        tag_slug = self.tag.slug

        with self.subTest("Проверить обычную ссылку на детальный просмотр тэга"):
            url = f"{TAG_DETAIL_URL}/{tag_slug}/"
            resolver_match = resolve(url)
            response = self.client.get(url)
            view_func = resolver_match.func.view_class
            self.assertEqual(view_func, TagDetailView)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Проверить имя ссылки на детальный просмотр тэга"):
            reverse_url = reverse(TAG_DETAIL_URL_NAME, kwargs={"slug": tag_slug})
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
        """
        Проверка на то, что в контекст запроса детального просмотра
        тэга добавляются фотографии и альбомы по данному тэгу.
        """
        tag_slug = self.tag.slug
        url = f"{TAG_DETAIL_URL}/{tag_slug}/"
        response = self.client.get(url)
        context = response.context

        with self.subTest("Альбомы с данным тэгом содержатся в контексте представления"):
            albums = Album.objects.filter(tags=self.tag)
            for album in albums:
                self.assertContains(response, album)
            self.assertEqual(albums.count(), len(context["albums"]))

        with self.subTest("Фотографии с данным тэгом содержатся в контексте представления"):
            photos = Photo.objects.filter(tags=self.tag)
            for photo in photos:
                self.assertContains(response, photo)
            self.assertEqual(photos.count(), len(context["photos"]))

        with self.subTest("Представление содержит полный набор тэгов галереи"):
            tags = Tag.objects.all()
            for tag in tags:
                self.assertContains(response, tag)
            self.assertEqual(tags.count(), len(context["tags"]))


class UploadFormViewTests(TestCase):
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
        test_dir = os.getenv("TEMP_ROOT")
        test_images_dir = Path(test_dir) / "gallery" / "photos"
        cls.test_image_paths = list_file_paths(test_images_dir)
        cls.album = Album.objects.create(name="Тестовый альбом")
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
            response = self.client.get(GALLERY_URL)
            self.assertContains(response, UPLOAD_URL)

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
            with Path(image_path).open("rb") as image:
                file = SimpleUploadedFile(name=image.name, content=image.read())
                photos.append(file)

        data = {"photos": photos, "album": self.album.pk}
        response = self.client.post(UPLOAD_URL, data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, GALLERY_URL)
        for photo in Photo.objects.all():
            self.assertEqual(photo.album, self.album)

    def test_upload_messages(self) -> None:
        """После загрузки фотографий появляется сообщение с результатом."""
        photos = []
        for image_path in self.test_image_paths:
            with Path(image_path).open("rb") as image:
                file = SimpleUploadedFile(name=image.name, content=image.read())
                photos.append(file)

        data = {"photos": photos, "album": self.album.pk}
        response = self.client.post(UPLOAD_URL, data, follow=True)
        self.assertTemplateUsed(response, "messages/alerts.html")

        photo_count = len(photos)
        url = self.album.get_absolute_url()
        name = self.album.name
        message = f'Загружено <b>{photo_count}</b> фотографий в альбом <a href="{url}" class="alert-link">{name}</a>'
        self.assertContains(response, message)

    def test_upload_image_verify(self) -> None:
        """Загружаемое изображение проверяется на валидность."""
        file = SimpleUploadedFile(
            name="test.pdf",
            content=bytes(get_random_string(12).encode()),
            content_type="application/pdf",
        )

        data = {"photos": [file], "album": self.album.pk}
        response = self.client.post(UPLOAD_URL, data, follow=True)
        message = f"Загруженный файл &quot;{file.name}&quot; не является изображением"
        self.assertContains(response, message)

        photos = Photo.objects.filter(album=self.album)
        self.assertFalse(photos.exists())

    def test_upload_view_context(self) -> None:
        """Представление содержит полный набор тэгов галереи."""
        response = self.client.get(UPLOAD_URL)
        context = response.context
        tags = Tag.objects.all()
        for tag in tags:
            self.assertContains(response, tag)
        self.assertEqual(tags.count(), len(context["tags"]))
