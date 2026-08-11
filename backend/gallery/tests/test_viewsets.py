"""Тесты API представлений галереи."""

from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APITestCase

from gallery.factories import AlbumFactory, PhotoFactory, TagFactory

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
        """Получение списка тегов."""
        url = "/api/gallery/tags/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 3)

        # Проверка структуры данных
        tag_data = response.data["results"][0]
        self.assertIn("name", tag_data)
        self.assertIn("slug", tag_data)
        self.assertIn("description", tag_data)

    def test_retrieve_tag(self) -> None:
        """Детальный просмотр тега."""
        url = f"/api/gallery/tags/{self.tag1.slug}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.tag1.name)
        self.assertEqual(response.data["slug"], self.tag1.slug)
        self.assertEqual(response.data["description"], self.tag1.description)

    def test_search_tags(self) -> None:
        """Поиск тегов по названию."""
        url = "/api/gallery/tags/"
        response = self.client.get(url, {"search": "природа"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "природа")

    def test_ordering_tags(self) -> None:
        """Сортировка тегов по имени."""
        url = "/api/gallery/tags/"
        response = self.client.get(url, {"ordering": "name"})
        self.assertEqual(response.status_code, 200)
        results = response.data["results"]
        names = [tag["name"] for tag in results]
        self.assertEqual(names, sorted(names))


class TestPhotoViewSet(APITestCase):
    """Тесты для PhotoViewSet."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)

        # Создать теги
        cls.tag1 = TagFactory(name="природа")
        cls.tag2 = TagFactory(name="закат")

        # Создать альбомы
        cls.album1 = AlbumFactory(name="Природа", public=True)
        cls.album2 = AlbumFactory(name="Город", public=False)

        # Создать фотографии
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
        """Получение списка фотографий неаутентифицированным пользователем - только публичные."""
        url = "/api/gallery/photos/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)  # Только публичная фотография
        self.assertEqual(response.data["results"][0]["name"], "Закат в горах")

    def test_list_photos_authenticated(self) -> None:
        """Получение списка фотографий аутентифицированным пользователем - только публичные."""
        self.client.force_authenticate(user=self.user)
        url = "/api/gallery/photos/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)  # Только публичная фотография

    def test_list_photos_staff_same_as_anonymous(self) -> None:
        """Получение списка фотографий staff пользователем - только публичные.

        Единая инварианта: staff и не-staff видят основной сайт одинаково.
        Административный доступ к скрытым объектам - через /admin/.
        """
        self.client.force_authenticate(user=self.staff_user)
        url = "/api/gallery/photos/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)  # Только публичная фотография

    def test_retrieve_public_photo(self) -> None:
        """Детальный просмотр публичной фотографии."""
        url = f"/api/gallery/photos/{self.photo1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Закат в горах")
        self.assertEqual(response.data["album"], self.album1.pk)
        self.assertIn("thumbnail_url", response.data)
        self.assertIn("preview_url", response.data)
        self.assertIn("image_url", response.data)
        self.assertEqual(len(response.data["tags"]), 2)

    def test_retrieve_private_photo_accessible_by_link(self) -> None:
        """Детальный просмотр приватной фотографии доступен по прямой ссылке (share-by-link).

        Единая инварианта: в list показываем только public=True, но retrieve
        любого объекта по прямой ссылке доступен всем пользователям.
        """
        url = f"/api/gallery/photos/{self.photo2.pk}/"
        # Аноним
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Ночной город")
        # Аутентифицированный не-staff
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Staff видит тот же набор, что и аноним
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Ночной город")

    def test_search_photos(self) -> None:
        """Поиск фотографий по названию, описанию и тегам."""
        url = "/api/gallery/photos/"
        response = self.client.get(url, {"search": "закат"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Закат в горах")

    def test_filter_photos_by_tag_slug(self) -> None:
        """Фильтрация фотографий по слагу тега."""
        url = "/api/gallery/photos/"
        response = self.client.get(url, {"tags__slug": self.tag1.slug})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Закат в горах")

    def test_ordering_photos(self) -> None:
        """Сортировка фотографий по дате съемки."""
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

        # Создать теги
        cls.tag1 = TagFactory(name="природа")
        cls.tag2 = TagFactory(name="путешествия")

        # Создать альбомы
        cls.album1 = AlbumFactory(name="Горные пейзажи", public=True)
        cls.album1.tags.add(cls.tag1, cls.tag2)
        cls.album2 = AlbumFactory(name="Личные фото", public=False)
        cls.album2.tags.add(cls.tag1)

        # Создать фотографии и обложку
        cls.photo1 = PhotoFactory(album=cls.album1, public=True)
        cls.photo2 = PhotoFactory(album=cls.album1, public=True)
        cls.album1.cover = cls.photo1
        cls.album1.save()

        cls.photo3 = PhotoFactory(album=cls.album2, public=False)
        cls.album2.cover = cls.photo3
        cls.album2.save()
        super().setUpTestData()

    def test_list_albums_unauthenticated(self) -> None:
        """Получение списка альбомов неаутентифицированным пользователем - только публичные."""
        url = "/api/gallery/albums/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)  # Только публичный альбом
        self.assertEqual(response.data["results"][0]["name"], "Горные пейзажи")

    def test_list_albums_authenticated(self) -> None:
        """Получение списка альбомов аутентифицированным пользователем - только публичные."""
        self.client.force_authenticate(user=self.user)
        url = "/api/gallery/albums/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)  # Только публичный альбом

    def test_list_albums_staff_same_as_anonymous(self) -> None:
        """Получение списка альбомов staff пользователем - только публичные.

        Единая инварианта: staff и не-staff видят основной сайт одинаково.
        Административный доступ к скрытым объектам - через /admin/.
        """
        self.client.force_authenticate(user=self.staff_user)
        url = "/api/gallery/albums/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)  # Только публичный альбом

    def test_retrieve_album(self) -> None:
        """Детальный просмотр альбома содержит фотографии."""
        url = f"/api/gallery/albums/{self.album1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Горные пейзажи")
        self.assertIn("cover_thumbnail_url", response.data)
        self.assertEqual(len(response.data["tags"]), 2)
        self.assertIn("photos", response.data)
        self.assertEqual(len(response.data["photos"]), 2)

    def test_search_albums(self) -> None:
        """Поиск альбомов по названию и описанию."""
        url = "/api/gallery/albums/"
        response = self.client.get(url, {"search": "Горные"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Горные пейзажи")

    def test_filter_albums_by_tag_slug(self) -> None:
        """Фильтрация альбомов по слагу тега."""
        url = "/api/gallery/albums/"
        response = self.client.get(url, {"tags__slug": self.tag1.slug})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Горные пейзажи")

    def test_ordering_albums(self) -> None:
        """Сортировка альбомов по порядку и дате создания."""
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
        """API-эндпоинт для альбома возвращает вложенные фотографии."""
        url = f"/api/gallery/albums/{self.album1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("photos", response.data)
        self.assertEqual(len(response.data["photos"]), 2)

    def test_retrieve_public_album_excludes_unpublished_photos(self) -> None:
        """Вложенные фотографии публичного альбома не содержат скрытые.

        Единая инварианта: в list-представлениях (включая вложенные) показываем
        только public=True. По прямой ссылке скрытой фотографии можно пройти
        в её детальный просмотр, но в листинге альбома она не появляется.
        """
        # Добавляем в публичный альбом одну скрытую фотографию
        PhotoFactory(album=self.album1, public=False)
        url = f"/api/gallery/albums/{self.album1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        photos = response.data["photos"]
        # Только 2 исходные публичные фотографии альбома, скрытая не попала
        self.assertEqual(len(photos), 2)
        for photo in photos:
            self.assertTrue(photo["public"])

    def test_retrieve_private_album_accessible_by_link(self) -> None:
        """Детальный просмотр приватного альбома доступен по прямой ссылке (share-by-link)."""
        url = f"/api/gallery/albums/{self.album2.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Личные фото")
        # Вложенные фото тоже фильтруются по public
        self.assertIsInstance(response.data["photos"], list)


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
        self.assertEqual(len(response.data["results"]), 3)
        for result in response.data["results"]:
            self.assertTrue(result["success"])
            self.assertIn("id", result)

    def test_upload_staff_mixed_files(self) -> None:
        """Загрузка смешанных файлов (валидные и невалидные) staff пользователем."""
        self.client.force_authenticate(user=self.staff_user)
        valid_file = self._create_test_image("valid_image.jpg", "green")
        invalid_file = self._create_invalid_file("invalid_file.txt", b"Not an image")
        response = self.client.post(self.url, {"album_id": self.album.id, "photos": [valid_file, invalid_file]})
        self.assertEqual(response.status_code, 201)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

        # Найти результаты по имени файла
        results_by_filename = {r["filename"]: r for r in response.data["results"]}
        self.assertTrue(results_by_filename["valid_image.jpg"]["success"])
        self.assertFalse(results_by_filename["invalid_file.txt"]["success"])
        self.assertEqual(results_by_filename["invalid_file.txt"]["error"], "Not an image")
