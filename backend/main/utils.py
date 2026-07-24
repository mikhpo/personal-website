"""Утилиты для генерации данных для React компонентов."""

from typing import TypedDict

from django.core.paginator import Page
from django.http import HttpRequest


class PaginationData(TypedDict):
    """Типизированный словарь для данных пагинации."""

    currentPage: int
    totalPages: int
    baseUrl: str


def get_pagination_data(request: HttpRequest, page_obj: Page | None) -> PaginationData | None:
    """
    Генерирует данные для React компонента пагинации.

    Args:
        request: HTTP запрос
        page_obj: Объект страницы из Django пагинатора (может быть None)

    Returns:
        Словарь с данными для React компонента пагинации или None, если page_obj отсутствует
    """
    # Если page_obj отсутствует, возвращаем None
    if page_obj is None:
        return None

    # Получаем базовый URL без параметров страницы
    base_url = request.path

    # Текущая страница и общее количество страниц
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages

    return PaginationData(
        currentPage=current_page,
        totalPages=total_pages,
        baseUrl=base_url,
    )
