"""Кастомные классы пагинации для REST API."""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Стандартная пагинация для списков."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class GalleryPhotoPagination(PageNumberPagination):
    """Пагинация для списка фотографий галереи."""

    page_size = 40
    page_size_query_param = "page_size"
    max_page_size = 100


class BlogArticlePagination(PageNumberPagination):
    """Пагинация для списка статей блога."""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50
