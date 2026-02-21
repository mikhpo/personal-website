"""Процессоры контекста для глобальных данных шаблонов."""

from typing import TYPE_CHECKING, TypedDict

from django.contrib.messages import get_messages
from django.db.models import QuerySet
from django.http import HttpRequest

from gallery.models import Tag

if TYPE_CHECKING:
    from django.contrib.messages.storage.base import Message


class NavbarLinkDropdown(TypedDict, total=False):
    """Тип для элементов выпадающего меню навигационной панели."""

    url: str
    text: str
    offcanvas: bool


class NavbarLink(TypedDict, total=False):
    """Тип для элементов навигационной панели."""

    url: str
    text: str
    active: bool
    dropdown: list[NavbarLinkDropdown]


class NavbarData(TypedDict):
    """Тип для данных навигационной панели."""

    brandName: str
    brandUrl: str
    links: list[NavbarLink]
    userAuthenticated: bool
    userName: str
    userIsStaff: bool


class AlertMessage(TypedDict, total=False):
    """Тип для сообщений системы оповещения."""

    message: str
    level: str
    dismissible: bool
    autoClose: bool
    autoCloseDelay: int


class AlertsData(TypedDict):
    """Тип для данных системы оповещения."""

    messages: list[AlertMessage]


class ContextNavbarData(TypedDict):
    """Тип для контекста навигационной панели."""

    navbar_data: NavbarData


class ContextTagsData(TypedDict):
    """Тип для контекста тегов."""

    tags: QuerySet[Tag]


class ContextAlertsData(TypedDict):
    """Тип для контекста системы оповещения."""

    alerts_data: AlertsData


# Время автоматического закрытия сообщений (в миллисекундах)
DEFAULT_AUTO_CLOSE_DELAY = 60000  # 1 минута


def navbar_data(request: HttpRequest) -> ContextNavbarData:
    """
    Процессор контекста для данных навигационной панели.

    Args:
        request: HTTP запрос

    Returns:
        Словарь с данными для navbar
    """
    # Базовые ссылки
    links: list[NavbarLink] = [
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
    ]

    # Логика для ссылки "Галерея" - показываем dropdown только находясь в разделе галереи
    if request.path.startswith("/gallery/"):
        gallery_link_with_dropdown: NavbarLink = {
            "url": "/gallery/",
            "text": "Галерея",
            "active": True,
            "dropdown": [
                {"url": "/gallery/albums/", "text": "Альбомы"},
                {"url": "/gallery/photos/", "text": "Фотографии"},
                {"url": "#", "text": "Тэги", "offcanvas": True},
            ],
        }
        links.append(gallery_link_with_dropdown)
    else:
        gallery_link: NavbarLink = {
            "url": "/gallery/",
            "text": "Галерея",
            "active": request.path.startswith("/gallery/"),
        }
        links.append(gallery_link)

    links.append(gallery_link)

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


def tags_data(request: HttpRequest) -> ContextTagsData:  # noqa: ARG001
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


def alerts_data(request: HttpRequest) -> ContextAlertsData:
    """
    Процессор контекста для системных сообщений.

    Args:
        request: HTTP запрос

    Returns:
        Словарь с сообщениями для отображения
    """
    messages: list[Message] = list(get_messages(request))
    alerts: list[AlertMessage] = []

    for message in messages:
        # Преобразуем уровни сообщений Django в уровни Bootstrap
        level_map = {
            "debug": "info",
            "info": "info",
            "success": "success",
            "warning": "warning",
            "error": "danger",
        }

        alert: AlertMessage = {
            "message": message.message,
            "level": level_map.get(message.tags, "info") if message.tags else "info",
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
