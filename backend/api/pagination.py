"""Кастомные классы пагинации для REST API."""

from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class BasePagination(PageNumberPagination):
    """Базовая пагинация для списков."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data: list[Any]) -> Response:
        """Возвращает ответ пагинации с полем total_pages."""
        if self.page is None:
            msg = "Объект страницы не задан. Сначала вызовите paginate_queryset."
            raise ValueError(msg)

        response = super().get_paginated_response(data)
        response.data["total_pages"] = self.page.paginator.num_pages
        return response

    def get_paginated_response_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Дополняет OpenAPI-схему ответа пагинации полем total_pages."""
        result = super().get_paginated_response_schema(schema)
        result["properties"]["total_pages"] = {"type": "integer", "example": 7}
        result["required"].append("total_pages")
        return result


class GalleryPhotoPagination(BasePagination):
    """Пагинация для списка фотографий галереи."""

    page_size = 40
    page_size_query_param = "page_size"
    max_page_size = 100


class BlogArticlePagination(BasePagination):
    """Пагинация для списка статей блога."""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50
