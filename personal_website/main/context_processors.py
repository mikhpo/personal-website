"""Процессоры контекста для глобальных данных шаблонов."""

from typing import Any

from django.contrib.messages import get_messages
from django.http import HttpRequest

from gallery.models import Tag

# Время автоматического закрытия сообщений (в миллисекундах)
DEFAULT_AUTO_CLOSE_DELAY = 60000  # 1 минута


def navbar_data(request: HttpRequest) -> dict[str, Any]:
    """
    Процессор контекста для данных навигационной панели.

    Args:
        request: HTTP запрос

    Returns:
        Словарь с данными для navbar
    """
    links = [
        {
            "url": "/",
            "text": "Главная",
            "active": "/main/" in request.path or request.path == "/",
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
                {"url": "#", "text": "Тэги", "offcanvas": True},
            ],
        },
    ]

    return {
        "navbar_data": {
            "brandName": "Mikhail Polyakov",
            "brandUrl": "/",
            "links": links,
            "userAuthenticated": request.user.is_authenticated,
            "userName": request.user.username if request.user.is_authenticated else "",
            "userIsStaff": request.user.is_staff if request.user.is_authenticated else False,
        },
    }


def tags_data(request: HttpRequest) -> dict[str, Any]:  # noqa: ARG001
    """
    Процессор контекста для данных тегов.

    Args:
        request: HTTP запрос

    Returns:
        Словарь с тегами для offcanvas панели
    """
    return {
        "tags": Tag.objects.all(),
    }


def alerts_data(request: HttpRequest) -> dict[str, Any]:
    """
    Процессор контекста для системных сообщений.

    Args:
        request: HTTP запрос

    Returns:
        Словарь с сообщениями для отображения
    """
    messages = get_messages(request)
    alerts = []

    for message in messages:
        # Преобразуем уровни сообщений Django в уровни Bootstrap
        level_map = {
            "debug": "info",
            "info": "info",
            "success": "success",
            "warning": "warning",
            "error": "danger",
        }

        alert = {
            "message": message.message,
            "level": level_map.get(message.tags, "info"),
            "dismissible": True,
            "autoClose": True,
            "autoCloseDelay": DEFAULT_AUTO_CLOSE_DELAY,
        }
        alerts.append(alert)

    return {
        "alerts_data": {
            "messages": alerts,
        },
    }
