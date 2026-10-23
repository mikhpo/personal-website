"""Тесты API представлений галереи."""

from io import BytesIO
from unittest import skipUnless

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from PIL import Image
from rest_framework.test import APITestCase

from gallery.factories import AlbumFactory, PhotoFactory, TagFactory
from gallery.models import Album, Photo, Tag

User = get_user_model()


class TestTagViewSet(APITestCase):
    """Тесты для TagViewSet."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.tag1 = TagFactory(name="природа", description="Фотографии природы")
        cls.tag2 = TagFactory(name="город", description="Городские пейзажи")
        cls.tag3 = TagFactory(name="люди", description="Фотографии людей")
        super().setUpTestData()

    def test_list_tags(self) -> None:
        """Список тегов содержит все созданные теги с полями name, slug и description."""
        url = "/api/gallery/tags/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Tag.objects.count())

        tag_data = response.data[0]
        self.assertIn("name", tag_data)
        self.assertIn("slug", tag_data)
        self.assertIn("description", tag_data)

    def test_retrieve_tag(self) -> None:
        """Детальный ответ тега возвращает его поля."""
        url = f"/api/gallery/tags/{self.tag1.slug}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.tag1.name)
        self.assertEqual(response.data["slug"], self.tag1.slug)
        self.assertEqual(response.data["description"], self.tag1.description)

    def test_search_tags(self) -> None:
        """Поиск по названию возвращает только совпадающие теги."""
        url = "/api/gallery/tags/"
        response = self.client.get(url, {"search": "природа"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([tag["name"] for tag in response.data], [self.tag1.name])

    def test_ordering_tags(self) -> None:
        """Сортировка по имени упорядочивает теги по возрастанию."""
        url = "/api/gallery/tags/"
        response = self.client.get(url, {"ordering": "name"})
        self.assertEqual(response.status_code, 200)
        names = [tag["name"] for tag in response.data]
        self.assertEqual(names, sorted(names))

    def test_list_tags_without_pagination(self) -> None:
        """Список отдает все теги одной выдачей, без разбиения на страницы."""
        base_count = Tag.objects.count()
        extra_tags = 25
        for number in range(extra_tags):
            TagFactory(name=f"тег-{number}")
        response = self.client.get("/api/gallery/tags/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Tag.objects.count())
        self.assertEqual(Tag.objects.count(), base_count + extra_tags)


class TestPhotoViewSet(APITestCase):
    """Тесты для PhotoViewSet."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)

        cls.tag1 = TagFactory(name="природа")
        cls.tag2 = TagFactory(name="закат")

        cls.album1 = AlbumFactory(name="Природа", public=True)
        cls.album2 = AlbumFactory(name="Город", public=False)

        cls.photo1 = PhotoFactory(
            name="Закат в горах",
            album=cls.album1,
            public=True,
        )
        cls.photo1.tags.add(cls.tag1, cls.tag2)

        cls.photo2 = PhotoFactory(
            name="Ночной город",
            album=cls.album2,
            public=False,
        )
        cls.photo2.tags.add(cls.tag1)
        super().setUpTestData()

    def test_list_photos_unauthenticated(self) -> None:
        """Список фотографий показывает анониму только публичные."""
        url = "/api/gallery/photos/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], Photo.objects.filter(public=True).count())
        self.assertEqual(response.data["results"][0]["name"], self.photo1.name)

    def test_list_photos_authenticated(self) -> None:
        """Список фотографий показывает аутентифицированному не-staff только публичные."""
        self.client.force_authenticate(user=self.user)
        url = "/api/gallery/photos/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], Photo.objects.filter(public=True).count())

    def test_list_photos_staff_same_as_anonymous(self) -> None:
        """Список фотографий для staff совпадает с анонимным: только публичные."""
        self.client.force_authenticate(user=self.staff_user)
        url = "/api/gallery/photos/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], Photo.objects.filter(public=True).count())

    def test_retrieve_public_photo(self) -> None:
        """Детальный ответ публичной фотографии содержит альбом, теги и URL изображений."""
        url = f"/api/gallery/photos/{self.photo1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.photo1.name)
        self.assertEqual(response.data["album"], self.album1.pk)
        self.assertEqual(response.data["album_name"], self.album1.name)
        self.assertIn("thumbnail_url", response.data)
        self.assertIn("preview_url", response.data)
        self.assertIn("image_url", response.data)
        self.assertEqual({tag["name"] for tag in response.data["tags"]}, {self.tag1.name, self.tag2.name})

    def test_retrieve_photo_contains_neighbor_ids(self) -> None:
        """Детальный ответ фотографии содержит id соседей по альбому."""
        url = f"/api/gallery/photos/{self.photo1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("previous_id", response.data)
        self.assertIn("next_id", response.data)

    def test_list_photos_have_no_neighbor_ids(self) -> None:
        """Список фотографий не вычисляет соседей."""
        response = self.client.get("/api/gallery/photos/")
        self.assertEqual(response.status_code, 200)
        for item in response.data["results"]:
            self.assertNotIn("previous_id", item)
            self.assertNotIn("next_id", item)

    def test_retrieve_private_photo_accessible_by_link(self) -> None:
        """Приватная фотография доступна по прямой ссылке.

        В list показываем только public=True, но retrieve любого объекта
        по прямой ссылке доступен всем пользователям.
        """
        url = f"/api/gallery/photos/{self.photo2.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.photo2.name)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.photo2.name)

    def test_search_photos(self) -> None:
        """Поиск находит фотографию по слову в названии или описании."""
        url = "/api/gallery/photos/"
        response = self.client.get(url, {"search": "Закат"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual([item["name"] for item in response.data["results"]], [self.photo1.name])

    @skipUnless(connection.vendor == "postgresql", "регистронезависимость кириллицы обеспечивает ILIKE PostgreSQL")
    def test_search_photos_case_insensitive(self) -> None:
        """Поиск находит фотографию запросом в другом регистре."""
        url = "/api/gallery/photos/"
        response = self.client.get(url, {"search": "закат"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual([item["name"] for item in response.data["results"]], [self.photo1.name])

    def test_search_photos_ignores_tags(self) -> None:
        """Поиск не сопоставляет фотографии по имени тега: теги вне search_fields."""
        photo = PhotoFactory(name="Опушка леса", description="Тихое утро в лесу", album=self.album1, public=True)
        photo.tags.add(self.tag1)
        url = "/api/gallery/photos/"
        response = self.client.get(url, {"search": self.tag1.name})
        self.assertEqual(response.status_code, 200)
        names = [item["name"] for item in response.data["results"]]
        self.assertNotIn(photo.name, names)

    def test_filter_photos_by_tag_slug(self) -> None:
        """Фильтр по слагу тега возвращает только публичные фотографии тега."""
        url = "/api/gallery/photos/"
        response = self.client.get(url, {"tags__slug": self.tag1.slug})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual([item["name"] for item in response.data["results"]], [self.photo1.name])

    def test_ordering_photos(self) -> None:
        """Эндпоинт принимает сортировку по дате съемки."""
        url = "/api/gallery/photos/"
        response = self.client.get(url, {"ordering": "-taken_at"})
        self.assertEqual(response.status_code, 200)


class TestAlbumViewSet(APITestCase):
    """Тесты для AlbumViewSet."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)

        cls.tag1 = TagFactory(name="природа")
        cls.tag2 = TagFactory(name="путешествия")

        cls.album1 = AlbumFactory(name="Горные пейзажи", public=True)
        cls.album1.tags.add(cls.tag1, cls.tag2)
        cls.album2 = AlbumFactory(name="Личные фото", public=False)
        cls.album2.tags.add(cls.tag1)

        cls.photo1 = PhotoFactory(album=cls.album1, public=True)
        cls.photo2 = PhotoFactory(album=cls.album1, public=True)
        cls.album1.cover = cls.photo1
        cls.album1.save()

        cls.photo3 = PhotoFactory(album=cls.album2, public=False)
        cls.album2.cover = cls.photo3
        cls.album2.save()
        super().setUpTestData()

    def test_list_albums_unauthenticated(self) -> None:
        """Список альбомов показывает анониму только публичные."""
        url = "/api/gallery/albums/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], Album.objects.filter(public=True).count())
        self.assertEqual(response.data["results"][0]["name"], self.album1.name)

    def test_list_albums_authenticated(self) -> None:
        """Список альбомов показывает аутентифицированному не-staff только публичные."""
        self.client.force_authenticate(user=self.user)
        url = "/api/gallery/albums/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], Album.objects.filter(public=True).count())

    def test_list_albums_staff_same_as_anonymous(self) -> None:
        """Список альбомов для staff совпадает с анонимным: только публичные."""
        self.client.force_authenticate(user=self.staff_user)
        url = "/api/gallery/albums/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], Album.objects.filter(public=True).count())

    def test_retrieve_album(self) -> None:
        """Детальный ответ альбома содержит обложку, теги и вложенные фотографии."""
        url = f"/api/gallery/albums/{self.album1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.album1.name)
        self.assertIn("cover_thumbnail_url", response.data)
        self.assertEqual({tag["name"] for tag in response.data["tags"]}, {self.tag1.name, self.tag2.name})
        self.assertIn("photos", response.data)
        self.assertEqual({photo["id"] for photo in response.data["photos"]}, {self.photo1.pk, self.photo2.pk})

    def test_search_albums(self) -> None:
        """Поиск находит альбом по слову в названии или описании."""
        url = "/api/gallery/albums/"
        response = self.client.get(url, {"search": "Горные"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual([item["name"] for item in response.data["results"]], [self.album1.name])

    def test_filter_albums_by_tag_slug(self) -> None:
        """Фильтр по слагу тега возвращает только публичные альбомы тега."""
        url = "/api/gallery/albums/"
        response = self.client.get(url, {"tags__slug": self.tag1.slug})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual([item["name"] for item in response.data["results"]], [self.album1.name])

    def test_ordering_albums(self) -> None:
        """Эндпоинт принимает сортировку по порядку и дате создания."""
        url = "/api/gallery/albums/"
        response = self.client.get(url, {"ordering": "order,-created_at"})
        self.assertEqual(response.status_code, 200)

    def test_list_albums_browsable_html(self) -> None:
        """Browsable API (HTML) списка альбомов отдаёт 200.

        Регрессия: BrowsableAPIRenderer строит filter-форму для filterset_fields
        через шаблон django_filters/rest_framework/crispy_form.html. Без django_filters
        в INSTALLED_APPS шаблон не обнаруживается и возникает TemplateDoesNotExist (500).
        """
        url = "/api/gallery/albums/"
        response = self.client.get(url, HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response["Content-Type"])

    def test_album_viewset_returns_nested_photos(self) -> None:
        """Эндпоинт альбома возвращает вложенные фотографии."""
        url = f"/api/gallery/albums/{self.album1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("photos", response.data)
        self.assertEqual({photo["id"] for photo in response.data["photos"]}, {self.photo1.pk, self.photo2.pk})

    def test_retrieve_public_album_excludes_unpublished_photos(self) -> None:
        """Вложенные фотографии публичного альбома не содержат скрытые.

        В list-представлениях (включая вложенные) показываем только public=True.
        По прямой ссылке скрытой фотографии можно пройти в её детальный просмотр,
        но в листинге альбома она не появляется.
        """
        PhotoFactory(album=self.album1, public=False)
        url = f"/api/gallery/albums/{self.album1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        photos = response.data["photos"]
        self.assertEqual({photo["id"] for photo in photos}, {self.photo1.pk, self.photo2.pk})

    def test_retrieve_private_album_accessible_by_link(self) -> None:
        """Детальный просмотр приватного альбома доступен по прямой ссылке."""
        url = f"/api/gallery/albums/{self.album2.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.album2.name)
        self.assertEqual(response.data["photos"], [])


@pytest.mark.skipif(connection.vendor != "postgresql", reason="Полнотекстовый поиск работает только на PostgreSQL")
class TestGalleryFullTextSearch(APITestCase):
    """Полнотекстовый поиск галереи: морфология и релевантность на PostgreSQL."""

    def test_album_morphology_finds_word_forms(self) -> None:
        """Запрос "путешествие" находит альбом со словом "Путешествия"."""
        album = AlbumFactory(name="Дальние края", description="Путешествия по миру", public=True)
        url = "/api/gallery/albums/"
        response = self.client.get(url, {"search": "путешествие"})
        self.assertEqual(response.status_code, 200)
        names = [item["name"] for item in response.data["results"]]
        self.assertIn(album.name, names)

    def test_photo_morphology_finds_word_forms(self) -> None:
        """Запрос "гора" находит фотографию со словом "Горы"."""
        album = AlbumFactory(name="Кавказ", public=True)
        photo = PhotoFactory(name="Горы Кавказа", description="Виды с перевалов", album=album, public=True)
        url = "/api/gallery/photos/"
        response = self.client.get(url, {"search": "гора"})
        self.assertEqual(response.status_code, 200)
        names = [item["name"] for item in response.data["results"]]
        self.assertIn(photo.name, names)

    def test_photo_relevance_name_above_description(self) -> None:
        """Фотография с совпадением в названии ранжируется выше совпадения в описании."""
        album = AlbumFactory(name="Прогулки", public=True)
        name_match = PhotoFactory(name="Велосипед", description="Прогулка по аллее", album=album, public=True)
        description_match = PhotoFactory(name="Аллея", description="Велосипед у входа", album=album, public=True)
        url = "/api/gallery/photos/"
        response = self.client.get(url, {"search": "велосипед"})
        self.assertEqual(response.status_code, 200)
        names = [item["name"] for item in response.data["results"]]
        self.assertEqual(names, [name_match.name, description_match.name])


class TestUploadViewSet(APITestCase):
    """Тесты для UploadViewSet."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)
        cls.album = AlbumFactory(name="Тестовый альбом", public=True)
        cls.url = "/api/gallery/upload/"
        super().setUpTestData()

    def _create_test_image(self, filename: str = "test_image.jpg", color: str = "red") -> SimpleUploadedFile:
        """Создать тестовое изображение для загрузки."""
        image_io = BytesIO()
        test_image = Image.new("RGB", (100, 100), color=color)
        test_image.save(image_io, format="JPEG")
        image_io.seek(0)
        return SimpleUploadedFile(
            filename,
            image_io.read(),
            content_type="image/jpeg",
        )

    def _create_invalid_file(
        self,
        filename: str = "invalid_file.jpg",
        content: bytes = b"Not an image",
    ) -> SimpleUploadedFile:
        """Создать невалидный файл (не изображение) для загрузки."""
        return SimpleUploadedFile(filename, content, content_type="image/jpeg")

    def test_upload_unauthenticated(self) -> None:
        """Загрузка фотографий неаутентифицированным пользователем - 401."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)

    def test_upload_authenticated_not_staff(self) -> None:
        """Загрузка фотографий обычным аутентифицированным пользователем - 403."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_upload_staff_no_album_id(self) -> None:
        """Загрузка фотографий staff пользователем без album_id - 400."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Album ID required")

    def test_upload_staff_album_not_found(self) -> None:
        """Загрузка фотографий staff пользователем с несуществующим album_id - 404."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.url, {"album_id": 99999})
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Album not found")

    def test_upload_staff_valid_album_no_files(self) -> None:
        """Загрузка фотографий staff пользователем без файлов - успех (пустой результат)."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.url, {"album_id": self.album.id})
        self.assertEqual(response.status_code, 201)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 0)

    def test_upload_staff_valid_album_with_valid_image(self) -> None:
        """Загрузка валидного изображения staff пользователем - успех."""
        self.client.force_authenticate(user=self.staff_user)
        upload_file = self._create_test_image("test_image.jpg", "red")
        response = self.client.post(self.url, {"album_id": self.album.id, "photos": [upload_file]})
        self.assertEqual(response.status_code, 201)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertTrue(response.data["results"][0]["success"])
        self.assertEqual(response.data["results"][0]["filename"], "test_image.jpg")
        self.assertIn("id", response.data["results"][0])

    def test_upload_staff_invalid_image(self) -> None:
        """Загрузка невалидного файла (не изображение) staff пользователем - ошибка."""
        self.client.force_authenticate(user=self.staff_user)
        upload_file = self._create_invalid_file("invalid_file.jpg")
        response = self.client.post(self.url, {"album_id": self.album.id, "photos": [upload_file]})
        self.assertEqual(response.status_code, 201)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertFalse(response.data["results"][0]["success"])
        self.assertEqual(response.data["results"][0]["filename"], "invalid_file.jpg")
        self.assertIn("error", response.data["results"][0])

    def test_upload_staff_multiple_images(self) -> None:
        """Загрузка нескольких изображений staff пользователем - успех."""
        self.client.force_authenticate(user=self.staff_user)
        files = [self._create_test_image(f"test_image_{i}.jpg", "blue") for i in range(3)]
        response = self.client.post(self.url, {"album_id": self.album.id, "photos": files})
        self.assertEqual(response.status_code, 201)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), len(files))
        for result in response.data["results"]:
            self.assertTrue(result["success"])
            self.assertIn("id", result)

    def test_upload_staff_mixed_files(self) -> None:
        """Загрузка смешанных файлов возвращает отдельный результат по каждому файлу."""
        self.client.force_authenticate(user=self.staff_user)
        files = [
            self._create_test_image("valid_image.jpg", "green"),
            self._create_invalid_file("invalid_file.txt", b"Not an image"),
        ]
        response = self.client.post(self.url, {"album_id": self.album.id, "photos": files})
        self.assertEqual(response.status_code, 201)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), len(files))

        results_by_filename = {r["filename"]: r for r in response.data["results"]}
        self.assertTrue(results_by_filename["valid_image.jpg"]["success"])
        self.assertFalse(results_by_filename["invalid_file.txt"]["success"])
        self.assertEqual(results_by_filename["invalid_file.txt"]["error"], "Not an image")
