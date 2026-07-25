"""Кастомные классы пагинации для REST API."""

from math import ceil
from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class BasePagination(PageNumberPagination):
    """Базовая пагинация для списков."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data: list[Any]) -> Response:
        """Возвращает ответ с дополнительным полем total_pages."""
        if self.page is None:
            msg = "Page object is not set. Call paginate_queryset first."
            raise ValueError(msg)

        request = self.request
        if request is None:
            msg = "Request object is not set."
            raise ValueError(msg)

        page_size = self.get_page_size(request)
        if page_size is None:
            msg = "Page size is not set."
            raise ValueError(msg)

        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": ceil(self.page.paginator.count / page_size),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            },
        )


class GalleryPhotoPagination(PageNumberPagination):
    """Пагинация для списка фотографий галереи."""

    page_size = 40
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data: list[Any]) -> Response:
        """Возвращает ответ с дополнительным полем total_pages."""
        if self.page is None:
            msg = "Page object is not set. Call paginate_queryset first."
            raise ValueError(msg)

        request = self.request
        if request is None:
            msg = "Request object is not set."
            raise ValueError(msg)

        page_size = self.get_page_size(request)
        if page_size is None:
            msg = "Page size is not set."
            raise ValueError(msg)

        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": ceil(self.page.paginator.count / page_size),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            },
        )


class BlogArticlePagination(PageNumberPagination):
    """Пагинация для списка статей блога."""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data: list[Any]) -> Response:
        """Возвращает ответ с дополнительным полем total_pages."""
        if self.page is None:
            msg = "Page object is not set. Call paginate_queryset first."
            raise ValueError(msg)

        request = self.request
        if request is None:
            msg = "Request object is not set."
            raise ValueError(msg)

        page_size = self.get_page_size(request)
        if page_size is None:
            msg = "Page size is not set."
            raise ValueError(msg)

        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": ceil(self.page.paginator.count / page_size),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            },
        )
