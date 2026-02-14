"""Тесты API представлений галереи."""

from django.contrib.auth import get_user_model
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

    def test_list_photos_staff(self) -> None:
        """Получение списка фотографий staff пользователем - все фотографии."""
        self.client.force_authenticate(user=self.staff_user)
        url = "/api/gallery/photos/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # Все фотографии

    def test_retrieve_public_photo(self) -> None:
        """Детальный просмотр публичной фотографии."""
        url = f"/api/gallery/photos/{self.photo1.slug}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Закат в горах")
        self.assertEqual(response.data["album"], self.album1.pk)
        self.assertIn("thumbnail_url", response.data)
        self.assertIn("preview_url", response.data)
        self.assertIn("image_url", response.data)
        self.assertEqual(len(response.data["tags"]), 2)

    def test_retrieve_private_photo_unauthenticated(self) -> None:
        """Детальный просмотр приватной фотографии неаутентифицированным пользователем - 404."""
        url = f"/api/gallery/photos/{self.photo2.slug}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_retrieve_private_photo_authenticated(self) -> None:
        """Детальный просмотр приватной фотографии обычным пользователем - 404."""
        self.client.force_authenticate(user=self.user)
        url = f"/api/gallery/photos/{self.photo2.slug}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_retrieve_private_photo_staff(self) -> None:
        """Детальный просмотр приватной фотографии staff пользователем - успех."""
        self.client.force_authenticate(user=self.staff_user)
        url = f"/api/gallery/photos/{self.photo2.slug}/"
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

    def test_filter_photos_by_album_slug(self) -> None:
        """Фильтрация фотографий по слагу альбома."""
        url = "/api/gallery/photos/"
        response = self.client.get(url, {"album__slug": self.album1.slug})
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
        """Сортировка фотографий по дате загрузки."""
        url = "/api/gallery/photos/"
        response = self.client.get(url, {"ordering": "-uploaded_at"})
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

    def test_list_albums_staff(self) -> None:
        """Получение списка альбомов staff пользователем - все альбомы."""
        self.client.force_authenticate(user=self.staff_user)
        url = "/api/gallery/albums/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # Все альбомы

    def test_retrieve_album(self) -> None:
        """Детальный просмотр альбома."""
        url = f"/api/gallery/albums/{self.album1.slug}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Горные пейзажи")
        self.assertIn("cover_thumbnail_url", response.data)
        self.assertEqual(len(response.data["tags"]), 2)

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
