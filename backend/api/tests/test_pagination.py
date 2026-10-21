"""Тесты для кастомных классов пагинации API."""

from typing import TYPE_CHECKING, cast

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
        """Размер страницы из query-параметра в пределах лимита применяется как есть."""
        page_size = 50
        request = Request(self.factory.get("/", {"page_size": page_size}))
        pagination = BasePagination()
        pagination.request = request

        self.assertEqual(pagination.get_page_size(request), page_size)

    def test_custom_page_size_exceeding_limit(self) -> None:
        """Размер страницы из query-параметра выше лимита обрезается до max_page_size."""
        request = Request(self.factory.get("/", {"page_size": BasePagination.max_page_size + 50}))
        pagination = BasePagination()
        pagination.request = request

        self.assertEqual(pagination.get_page_size(request), BasePagination.max_page_size)

    def test_paginated_response_includes_total_pages(self) -> None:
        """Ответ пагинации содержит все поля.

        count равен числу объектов, total_pages и размер результатов согласованы
        с размером страницы по умолчанию.
        """
        total_photos = 100
        for _ in range(total_photos):
            PhotoFactory.create()
        queryset: QuerySet[Photo] = Photo.objects.all()

        request = Request(self.factory.get("/"))
        pagination = BasePagination()
        pagination.request = request

        page = pagination.paginate_queryset(queryset, request)
        self.assertIsNotNone(page)

        response = pagination.get_paginated_response(cast("list[Photo]", page))

        self.assertIn("count", response.data)
        self.assertIn("total_pages", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        self.assertEqual(response.data["count"], total_photos)
        self.assertEqual(response.data["total_pages"], total_photos // BasePagination.page_size)
        self.assertEqual(len(response.data["results"]), BasePagination.page_size)

    def test_paginated_response_with_custom_page_size(self) -> None:
        """total_pages и размер результатов согласованы с размером страницы из query-параметра."""
        total_photos = 100
        for _ in range(total_photos):
            PhotoFactory.create()
        queryset: QuerySet[Photo] = Photo.objects.all()

        page_size = 10
        request = Request(self.factory.get("/", {"page_size": page_size}))
        pagination = BasePagination()
        pagination.request = request

        page = pagination.paginate_queryset(queryset, request)
        self.assertIsNotNone(page)

        response = pagination.get_paginated_response(cast("list[Photo]", page))

        self.assertEqual(response.data["count"], total_photos)
        self.assertEqual(response.data["total_pages"], total_photos // page_size)
        self.assertEqual(len(response.data["results"]), page_size)


class TestGalleryPhotoPagination(APITestCase):
    """Тесты для пагинации фотографий галереи."""

    def setUp(self) -> None:
        """Подготовка тестовых данных."""
        self.factory = APIRequestFactory()

    def test_large_page_size_exceeding_limit(self) -> None:
        """Размер страницы из query-параметра выше лимита обрезается до max_page_size."""
        request = Request(self.factory.get("/", {"page_size": GalleryPhotoPagination.max_page_size + 50}))
        pagination = GalleryPhotoPagination()
        pagination.request = request

        self.assertEqual(pagination.get_page_size(request), GalleryPhotoPagination.max_page_size)

    def test_paginated_response_total_pages(self) -> None:
        """Число страниц и результаты согласованы с размером страницы по умолчанию."""
        total_photos = 80
        for _ in range(total_photos):
            PhotoFactory.create()
        queryset: QuerySet[Photo] = Photo.objects.all()

        request = Request(self.factory.get("/"))
        pagination = GalleryPhotoPagination()
        pagination.request = request

        page = pagination.paginate_queryset(queryset, request)
        self.assertIsNotNone(page)

        response = pagination.get_paginated_response(cast("list[Photo]", page))

        self.assertEqual(response.data["count"], total_photos)
        self.assertEqual(response.data["total_pages"], total_photos // GalleryPhotoPagination.page_size)
        self.assertEqual(len(response.data["results"]), GalleryPhotoPagination.page_size)

    def test_paginated_response_with_custom_page_size(self) -> None:
        """Число страниц и результаты согласованы с размером страницы из query-параметра."""
        total_photos = 50
        for _ in range(total_photos):
            PhotoFactory.create()
        queryset: QuerySet[Photo] = Photo.objects.all()

        page_size = 25
        request = Request(self.factory.get("/", {"page_size": page_size}))
        pagination = GalleryPhotoPagination()
        pagination.request = request

        page = pagination.paginate_queryset(queryset, request)
        self.assertIsNotNone(page)

        response = pagination.get_paginated_response(cast("list[Photo]", page))

        self.assertEqual(response.data["count"], total_photos)
        self.assertEqual(response.data["total_pages"], total_photos // page_size)
        self.assertEqual(len(response.data["results"]), page_size)


class TestBlogArticlePagination(APITestCase):
    """Тесты для пагинации статей блога."""

    def setUp(self) -> None:
        """Подготовка тестовых данных."""
        self.factory = APIRequestFactory()

    def test_small_page_size(self) -> None:
        """Маленький размер страницы из query-параметра применяется как есть."""
        page_size = 2
        request = Request(self.factory.get("/", {"page_size": page_size}))
        pagination = BlogArticlePagination()
        pagination.request = request

        self.assertEqual(pagination.get_page_size(request), page_size)

    def test_page_size_exceeding_limit(self) -> None:
        """Размер страницы из query-параметра выше лимита обрезается до max_page_size."""
        request = Request(self.factory.get("/", {"page_size": BlogArticlePagination.max_page_size + 50}))
        pagination = BlogArticlePagination()
        pagination.request = request

        self.assertEqual(pagination.get_page_size(request), BlogArticlePagination.max_page_size)

    def test_paginated_response_total_pages(self) -> None:
        """Число страниц и результаты согласованы с размером страницы по умолчанию."""
        total_articles = 25
        for _ in range(total_articles):
            ArticleFactory.create()
        queryset: QuerySet[Article] = Article.objects.all()

        request = Request(self.factory.get("/"))
        pagination = BlogArticlePagination()
        pagination.request = request

        page = pagination.paginate_queryset(queryset, request)
        self.assertIsNotNone(page)

        response = pagination.get_paginated_response(cast("list[Article]", page))

        self.assertEqual(response.data["count"], total_articles)
        self.assertEqual(response.data["total_pages"], total_articles // BlogArticlePagination.page_size)
        self.assertEqual(len(response.data["results"]), BlogArticlePagination.page_size)

    def test_paginated_response_with_custom_page_size(self) -> None:
        """Число страниц и результаты согласованы с размером страницы из query-параметра."""
        total_articles = 30
        for _ in range(total_articles):
            ArticleFactory.create()
        queryset: QuerySet[Article] = Article.objects.all()

        page_size = 10
        request = Request(self.factory.get("/", {"page_size": page_size}))
        pagination = BlogArticlePagination()
        pagination.request = request

        page = pagination.paginate_queryset(queryset, request)
        self.assertIsNotNone(page)

        response = pagination.get_paginated_response(cast("list[Article]", page))

        self.assertEqual(response.data["count"], total_articles)
        self.assertEqual(response.data["total_pages"], total_articles // page_size)
        self.assertEqual(len(response.data["results"]), page_size)
