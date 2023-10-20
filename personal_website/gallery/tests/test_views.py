import os
import random
import shutil
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import QuerySet
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import resolve, reverse

from gallery.models import Album, Photo, Tag
from gallery.views import (
    AlbumDetailView,
    AlbumListView,
    GalleryHomeView,
    PhotoDetailView,
    PhotoListView,
    TagDetailView,
    TagListView,
    UploadFormView,
)
from personal_website.utils import list_image_paths

APP_NAME = "gallery"

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
TAG_LIST_URL = f"/{APP_NAME}/tags/"
TAG_LIST_URL_NAME = f"{APP_NAME}:tag-list"
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


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, "media"))
class GalleryViewsTest(TestCase):
    """
    Тестирование представлений галереи.
    """

    @classmethod
    def setUpTestData(cls):
        cls.tag = Tag.objects.create(name="Test tag")
        cls.album = Album.objects.create(name="Test album")
        cls.album.tags.add(cls.tag)
        images = list_image_paths()
        for image in images:
            photo = Photo.objects.create(image=image, album=cls.album)
            photo.tags.add(cls.tag)

    def check_gallery_mixin_content(self, response: HttpResponse):
        """
        Переиспользуемый метод проверки добавления контента
        в контекст представления с использованием миксина.
        """
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

    def test_gallery_home_url(self):
        """
        Проверить работоспособность ссылки на главную страницу галереи.
        """
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

    def test_gallery_home_view_context(self):
        """
        Проверить, что в контекст представления домашней страницы галереи
        автоматически добавляется контекст содержимого галереи.
        """
        response = self.client.get(GALLERY_URL)
        self.check_gallery_mixin_content(response)

    def test_photo_list_url(self):
        """
        Проверить работоспособность ссылки на просмотр всех фотографий.
        """
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

    def test_photo_detail_url(self):
        """
        Проверить работоспособность ссылки на детальный просмотр фотографии.
        """
        # Первичный ключ тестовой фотографии.
        first_photo = Photo.objects.first()
        photo_slug = first_photo.slug

        with self.subTest(
            "Проверить переход по ссылке для детального просмотра фотографии"
        ):
            photo_url = f"{PHOTO_DETAIL_URL}/{photo_slug}/"
            resolver_match = resolve(photo_url)
            response = self.client.get(photo_url)
            photo_url_func = resolver_match.func.view_class
            self.assertEqual(photo_url_func, PhotoDetailView)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest(
            "Проверить именную ссылку для детального просмотра фотографии"
        ):
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

    def test_photo_detail_view_context(self):
        """
        Проверить содержание представления для детального просмотра фотографии.
        """
        first_photo = Photo.objects.first()
        last_photo = Photo.objects.last()
        all_photos = Photo.objects.all()
        middle_photos = all_photos.exclude(pk__in=[first_photo.pk, last_photo.pk])
        middle_photo = random.choice(middle_photos)
        new_album = Album.objects.create(name="New test album")
        new_photo = Photo.objects.create(name="New photo", album=new_album)

        with self.subTest(
            "Для первой фотографии в альбоме доступа только ссылка на следующую фотографию"
        ):
            url = f"{PHOTO_DETAIL_URL}/{first_photo.slug}/"
            response = self.client.get(url)
            context = response.context
            self.assertIsNotNone(context["next_photo"])
            self.assertContains(response, "Следующая")
            self.assertIsNone(context["previous_photo"])
            self.assertNotContains(response, "Предыдущая")

        with self.subTest(
            "Для последней фотографии в альбоме доступна только ссылка на предыдущую фотографию"
        ):
            url = f"{PHOTO_DETAIL_URL}/{last_photo.slug}/"
            response = self.client.get(url)
            context = response.context
            self.assertIsNotNone(context["previous_photo"])
            self.assertContains(response, "Предыдущая")
            self.assertIsNone(context["next_photo"])
            self.assertNotContains(response, "Следующая")
            self.assertNotContains(response, new_photo.get_absolute_url())

        with self.subTest(
            "Для фотографии в середине альбома доступны и ссылка на "
            "следующую фотографию, и ссылка на предыдущую фотографию"
        ):
            url = f"{PHOTO_DETAIL_URL}/{middle_photo.slug}/"
            response = self.client.get(url)
            context = response.context
            self.assertIsNotNone(context["next_photo"])
            self.assertContains(response, "Следующая")
            self.assertIsNotNone(context["previous_photo"])
            self.assertContains(response, "Предыдущая")

    def test_album_detail_url(self):
        """
        Проверить работоспособность ссылки на детальный просмотр альбома.
        """
        # Слаг тестового альбома.
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

    def test_album_detail_view_context(self):
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
        context_photos: QuerySet[Photo] = context["photos"]
        for photo in public_photos:
            self.assertContains(response, photo)
        self.assertNotContains(response, private_photo)
        self.assertEqual(len(context_photos), public_photos.count())

    def test_album_list_url(self):
        """
        Проверить работоспособность ссылки на просмотр всех альбомов.
        """
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

    def test_album_list_context(self):
        """
        В списке альбомов должны отображаться только публичные альбомы.
        """
        with self.subTest("Публичный альбом отображается"):
            self.assertTrue(self.album.public)
            response = self.client.get(ALBUM_LIST_URL)
            self.assertContains(response, self.album)

        with self.subTest("Приватный альбом не отображается"):
            self.album.public = False
            self.album.save()
            response = self.client.get(ALBUM_LIST_URL)
            self.assertNotContains(response, self.album)

    def test_tag_detail_url(self):
        """
        Тестирование ссылки на детальный просмотр тега.
        """
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

    def test_tag_detail_view_context(self):
        """
        Проверка на то, что в контекст запроса детального просмотра
        тэга добавляются фотографии и альбомы по данному тэгу.
        """
        tag_slug = self.tag.slug
        url = f"{TAG_DETAIL_URL}/{tag_slug}/"
        response = self.client.get(url)
        context = response.context

        with self.subTest(
            "Альбомы с данным тэгом содержатся в контексте представления"
        ):
            albums = Album.objects.filter(tags=self.tag)
            for album in albums:
                self.assertContains(response, album)
            self.assertEqual(albums.count(), len(context["albums"]))

        with self.subTest(
            "Фотографии с данным тэгом содержатся в контексте представления"
        ):
            photos = Photo.objects.filter(tags=self.tag)
            for photo in photos:
                self.assertContains(response, photo)
            self.assertEqual(photos.count(), len(context["photos"]))

    def test_tag_list_url(self):
        """
        Проверка получения страницы по запросу списка тэгов.
        """
        with self.subTest("Проверка обычной ссылки на просмотр списка всех тегов"):
            resolver_match = resolve(TAG_LIST_URL)
            response = self.client.get(TAG_LIST_URL)
            url_view_class = resolver_match.func.view_class
            self.assertEqual(url_view_class, TagListView)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Проверка именной ссылки на просмотр списка всех тегов"):
            reverse_url = reverse(TAG_LIST_URL_NAME)
            reverse_resolver_match = resolve(reverse_url)
            reverse_response = self.client.get(reverse_url)
            reverse_url_view_class = reverse_resolver_match.func.view_class
            self.assertEqual(reverse_url_view_class, TagListView)
            self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
            self.assertEqual(url_view_class, reverse_url_view_class)

        with self.subTest("Проверка используемых представлением шаблонов"):
            self.assertEqual(response.templates, reverse_response.templates)
            self.assertTemplateUsed(response, TAG_LIST_TEMPLATE_NAME)
            self.assertTemplateUsed(response, BASE_TEMPLATE_NAME)


class UploadFormViewTests(TestCase):
    """
    Тесты формы для пакетной загрузки фотографий в альбом.
    """

    test_username = "test_username"
    staff_username = "staff_username"
    test_password = "test_password"
    staff_password = "staff_password"

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = User.objects.create_user(
            username=cls.test_username, password=cls.test_password
        )
        cls.staff_user = User.objects.create_superuser(
            username=cls.staff_username, password=cls.staff_password
        )
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        cls.test_image_paths = list_image_paths()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.staff_username, password=self.staff_password)

    def test_upload_url_resolve(self):
        """
        Стандартная ссылка корректно разрешается.
        """
        resolver_match = resolve(UPLOAD_URL)
        self.assertEqual(resolver_match.func.view_class, UploadFormView)

    def test_upload_url_name_resolve(self):
        """
        Имя ссылки разрешается корректно.
        """
        url = reverse(UPLOAD_URL_NAME)
        resolver_match = resolve(url)
        self.assertEqual(resolver_match.func.view_class, UploadFormView)

    def test_templates_used(self):
        """
        Проверка использованных представлением шаблонов.
        """
        response = self.client.get(UPLOAD_URL)
        for template in (UPLOAD_TEMPLATE_NAME, BASE_TEMPLATE_NAME):
            self.assertTemplateUsed(response, template)

    def test_response_status_code(self):
        """
        Проверить полученный статус HTTP-ответа.
        """
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

    def test_item_in_navbar(self):
        """
        Проверка показа ссылки на форму загрузки в навигационной панели.
        """
        with self.subTest("С главной страницы не доступна ссылка на форму загрузки"):
            response = self.client.get("/main/")
            self.assertNotContains(response, UPLOAD_URL)

        with self.subTest("Со страницы галереи доступна ссылка на форму загрузки"):
            response = self.client.get(GALLERY_URL)
            self.assertContains(response, UPLOAD_URL)

        with self.subTest(
            "Для пользователя с обычными правами не доступна ссылка на форму загрузки"
        ):
            self.client.login(username=self.test_username, password=self.test_password)
            response = self.client.get(GALLERY_URL)
            self.assertNotContains(response, UPLOAD_URL)

        with self.subTest(
            "Для пользователя, который не авторизован, не доступна ссылка на форму загрузки"
        ):
            self.client.logout()
            response = self.client.get(GALLERY_URL)
            self.assertNotContains(response, UPLOAD_URL)

    def test_images_upload(self):
        """
        Проверка результатов загрузки фотографий через форму.
        """
        album = Album.objects.create(name="Тестовый альбом")
        photos = []
        for image_path in self.test_image_paths:
            with open(image_path, "rb") as image:
                file = SimpleUploadedFile(name=image.name, content=image.read())
                photos.append(file)

        data = {"photos": photos, "album": album.pk}
        response = self.client.post(UPLOAD_URL, data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, GALLERY_URL)
        for photo in Photo.objects.all():
            self.assertEqual(photo.album, album)
