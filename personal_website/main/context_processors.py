"""Context processors для глобальных данных шаблонов."""

from typing import Any

from django.http import HttpRequest


def navbar_data(request: HttpRequest) -> dict[str, Any]:
    """
    Context processor для данных навигационной панели.

    Args:
        request: HTTP запрос

    Returns:
        Словарь с данными для navbar
    """
    links = [
        {
            "url": "/",
            "text": "Главная",
            "active": request.path == "/",
        },
        {
            "url": "/blog/",
            "text": "Блог",
            "active": request.path.startswith("/blog/"),
        },
        {
            "url": "/gallery/",
            "text": "Галерея",
            "active": request.path.startswith("/gallery/"),
            "dropdown": [
                {"url": "/gallery/albums/", "text": "Альбомы"},
                {"url": "/gallery/photos/", "text": "Фотографии"},
                {"url": "/gallery/tags/", "text": "Тэги"},
            ],
        },
    ]

    return {
        "navbar_data": {
            "brandName": "Personal Website",
            "brandUrl": "/",
            "links": links,
            "userAuthenticated": request.user.is_authenticated,
            "userName": request.user.username if request.user.is_authenticated else "",
            "userIsStaff": request.user.is_staff if request.user.is_authenticated else False,
        },
    }
