"""Тесты для кастомных классов пагинации API."""

from typing import TYPE_CHECKING, cast
from unittest.mock import Mock

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, APITestCase

from api.pagination import BasePagination, BlogArticlePagination, GalleryPhotoPagination
from blog.factories import ArticleFactory
from blog.models import Article
from gallery.factories import PhotoFactory
from gallery.models import Photo

if TYPE_CHECKING:
    from django.db.models import QuerySet


class TestBasePagination(APITestCase):
    """Тесты для базового класса пагинации."""

    def setUp(self) -> None:
        """Подготовка тестовых данных."""
        self.factory = APIRequestFactory()

    def test_custom_page_size_within_limit(self) -> None:
        """Тест пользовательского размера страницы в пределах лимита."""
        request = Request(self.factory.get("/", {"page_size": 50}))
        pagination = BasePagination()
        pagination.request = request

        self.assertEqual(pagination.get_page_size(request), 50)

    def test_custom_page_size_exceeding_limit(self) -> None:
        """Тест размера страницы больше максимального."""
        request = Request(self.factory.get("/", {"page_size": 150}))
        pagination = BasePagination()
        pagination.request = request

        self.assertEqual(pagination.get_page_size(request), 100)

    def test_paginated_response_includes_total_pages(self) -> None:
        """Тест проверки наличия поля total_pages в ответе пагинации."""
        request = Request(self.factory.get("/"))
        pagination = BasePagination()

        mock_page = Mock()
        mock_page.paginator.count = 100
        pagination.page = mock_page
        pagination.request = request

        response = pagination.get_paginated_response([{"id": 1}, {"id": 2}])

        self.assertIn("count", response.data)
        self.assertIn("total_pages", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        self.assertEqual(response.data["count"], 100)
        self.assertEqual(response.data["total_pages"], 5)
        self.assertEqual(response.data["results"], [{"id": 1}, {"id": 2}])

    def test_paginated_response_with_custom_page_size(self) -> None:
        """Тест проверки total_pages с кастомным размером страницы."""
        request = Request(self.factory.get("/", {"page_size": 10}))
        pagination = BasePagination()
        pagination.request = request

        mock_page = Mock()
        mock_page.paginator.count = 100
        pagination.page = mock_page

        response = pagination.get_paginated_response([{"id": 1}])

        self.assertEqual(response.data["total_pages"], 10)


class TestGalleryPhotoPagination(APITestCase):
    """Тесты для пагинации фотографий галереи."""

    def setUp(self) -> None:
        """Подготовка тестовых данных."""
        self.factory = APIRequestFactory()

    def test_large_page_size_exceeding_limit(self) -> None:
        """Тест размера страницы больше максимального."""
        request = Request(self.factory.get("/", {"page_size": 150}))
        pagination = GalleryPhotoPagination()
        pagination.request = request

        self.assertEqual(pagination.get_page_size(request), 100)

    def test_paginated_response_total_pages(self) -> None:
        """Тест проверки total_pages для пагинации галереи с реальными объектами."""
        # Создаем 80 фотографий (стандартный размер страницы = 40, должно получиться 2 страницы)
        for _ in range(80):
            PhotoFactory.create()
        queryset: QuerySet[Photo] = Photo.objects.all()

        request = Request(self.factory.get("/"))
        pagination = GalleryPhotoPagination()
        pagination.request = request

        # Применяем пагинацию к queryset
        page = pagination.paginate_queryset(queryset, request)
        self.assertIsNotNone(page)

        response = pagination.get_paginated_response(cast("list[Photo]", page))

        self.assertEqual(response.data["count"], 80)
        self.assertEqual(response.data["total_pages"], 2)
        self.assertEqual(len(response.data["results"]), 40)  # Первая страница

    def test_paginated_response_with_custom_page_size(self) -> None:
        """Тест проверки total_pages с кастомным размером страницы для галереи."""
        # Создаем 50 фотографий
        for _ in range(50):
            PhotoFactory.create()
        queryset: QuerySet[Photo] = Photo.objects.all()

        # Устанавливаем кастомный размер страницы = 25
        request = Request(self.factory.get("/", {"page_size": 25}))
        pagination = GalleryPhotoPagination()
        pagination.request = request

        # Применяем пагинацию к queryset
        page = pagination.paginate_queryset(queryset, request)
        self.assertIsNotNone(page)

        response = pagination.get_paginated_response(cast("list[Photo]", page))

        self.assertEqual(response.data["count"], 50)
        self.assertEqual(response.data["total_pages"], 2)
        self.assertEqual(len(response.data["results"]), 25)  # Первая страница


class TestBlogArticlePagination(APITestCase):
    """Тесты для пагинации статей блога."""

    def setUp(self) -> None:
        """Подготовка тестовых данных."""
        self.factory = APIRequestFactory()

    def test_small_page_size(self) -> None:
        """Тест маленького размера страницы."""
        request = Request(self.factory.get("/", {"page_size": 2}))
        pagination = BlogArticlePagination()
        pagination.request = request

        self.assertEqual(pagination.get_page_size(request), 2)

    def test_page_size_exceeding_limit(self) -> None:
        """Тест размера страницы больше максимального."""
        request = Request(self.factory.get("/", {"page_size": 100}))
        pagination = BlogArticlePagination()
        pagination.request = request

        self.assertEqual(pagination.get_page_size(request), 50)

    def test_paginated_response_total_pages(self) -> None:
        """Тест проверки total_pages для пагинации блога с реальными объектами."""
        # Создаем 25 статей (стандартный размер страницы = 5, должно получиться 5 страниц)
        for _ in range(25):
            ArticleFactory.create()
        queryset: QuerySet[Article] = Article.objects.all()

        request = Request(self.factory.get("/"))
        pagination = BlogArticlePagination()
        pagination.request = request

        # Применяем пагинацию к queryset
        page = pagination.paginate_queryset(queryset, request)
        self.assertIsNotNone(page)

        response = pagination.get_paginated_response(cast("list[Article]", page))

        self.assertEqual(response.data["count"], 25)
        self.assertEqual(response.data["total_pages"], 5)
        self.assertEqual(len(response.data["results"]), 5)  # Первая страница

    def test_paginated_response_with_custom_page_size(self) -> None:
        """Тест проверки total_pages с кастомным размером страницы для блога."""
        # Создаем 30 статей
        for _ in range(30):
            ArticleFactory.create()
        queryset: QuerySet[Article] = Article.objects.all()

        # Устанавливаем кастомный размер страницы = 10
        request = Request(self.factory.get("/", {"page_size": 10}))
        pagination = BlogArticlePagination()
        pagination.request = request

        # Применяем пагинацию к queryset
        page = pagination.paginate_queryset(queryset, request)
        self.assertIsNotNone(page)

        response = pagination.get_paginated_response(cast("list[Article]", page))

        self.assertEqual(response.data["count"], 30)
        self.assertEqual(response.data["total_pages"], 3)
        self.assertEqual(len(response.data["results"]), 10)  # Первая страница
