"""Тесты для кастомных классов пагинации API."""

from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from api.pagination import BlogArticlePagination, GalleryPhotoPagination, StandardResultsSetPagination


class TestPagination(TestCase):
    """Тесты для классов пагинации."""

    def setUp(self) -> None:
        """Подготовка тестовых данных."""
        self.factory = APIRequestFactory()

    def test_standard_pagination_with_custom_page_size_within_limit(self) -> None:
        """Тест стандартной пагинации с пользовательским размером страницы в пределах лимита."""
        request = Request(self.factory.get("/", {"page_size": 50}))
        pagination = StandardResultsSetPagination()
        pagination.request = request

        # Проверяем, что размер страницы может быть установлен в пределах max_page_size
        self.assertEqual(pagination.get_page_size(request), 50)

    def test_standard_pagination_with_custom_page_size_exceeding_limit(self) -> None:
        """Тест стандартной пагинации с размером страницы больше максимального."""
        request = Request(self.factory.get("/", {"page_size": 150}))
        pagination = StandardResultsSetPagination()
        pagination.request = request

        # Проверяем, что размер страницы ограничен максимальным значением
        self.assertEqual(pagination.get_page_size(request), 100)

    def test_gallery_pagination_with_large_page_size(self) -> None:
        """Тест пагинации галереи с размером страницы больше максимального."""
        request = Request(self.factory.get("/", {"page_size": 150}))
        pagination = GalleryPhotoPagination()
        pagination.request = request

        # Проверяем, что размер страницы ограничен максимальным значением
        self.assertEqual(pagination.get_page_size(request), 100)

    def test_blog_pagination_with_small_page_size(self) -> None:
        """Тест пагинации блога с маленьким размером страницы."""
        request = Request(self.factory.get("/", {"page_size": 2}))
        pagination = BlogArticlePagination()
        pagination.request = request

        # Проверяем, что можно установить меньший размер страницы
        self.assertEqual(pagination.get_page_size(request), 2)

    def test_blog_pagination_with_page_size_exceeding_limit(self) -> None:
        """Тест пагинации блога с размером страницы больше максимального."""
        request = Request(self.factory.get("/", {"page_size": 100}))
        pagination = BlogArticlePagination()
        pagination.request = request

        # Проверяем, что размер страницы ограничен максимальным значением
        self.assertEqual(pagination.get_page_size(request), 50)
