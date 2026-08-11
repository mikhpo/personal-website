"""Кастомные permissions для REST API."""

from typing import TYPE_CHECKING

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View

if TYPE_CHECKING:
    from django.db.models import Model


class IsPublicOrAuthor(permissions.BasePermission):
    """
    Permission класс для объектов с полем public.

    Правило публичности объектов проекта (gallery: Album, Photo; blog: Article,
    Category, Topic, Series): в list/индексе/sitemap показываются только объекты
    с public=True, но детальный просмотр (retrieve/detail) любого объекта по
    прямой ссылке доступен всем пользователям (share-by-link). Этот permission
    разрешает все безопасные методы; фильтрация публичных объектов в списках
    выполняется на уровне get_queryset() соответствующего view.

    Write-path остаётся без изменений: модификация/удаление — только для staff
    или автора; создание — для аутентифицированных.

    Модель должна иметь поля:
    - public: BooleanField
    - author: ForeignKey к User (опционально)
    """

    def has_permission(self, request: Request, view: View) -> bool:  # noqa: ARG002
        """
        Проверка прав доступа на уровне view.

        Args:
            request: HTTP запрос
            view: View, обрабатывающая запрос

        Returns:
            True если доступ разрешен, False иначе
        """
        # Для операций чтения разрешаем доступ всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для операций создания/модификации требуется аутентификация
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Request, view: View, obj: "Model") -> bool:  # noqa: ARG002
        """
        Проверка прав доступа к конкретному объекту.

        Args:
            request: HTTP запрос
            view: View, обрабатывающая запрос
            obj: Объект модели

        Returns:
            True если доступ разрешен, False иначе
        """
        # Администраторы имеют полный доступ ко всем операциям
        user = request.user
        if isinstance(user, AbstractBaseUser) and user.is_staff:
            return True

        # Для чтения разрешаем доступ к любому объекту: видимость публичных
        # в списках регулируется на уровне get_queryset() view.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для модификации и удаления требуется авторство или админ права
        # Если у объекта есть автор, проверяем авторство
        if hasattr(obj, "author"):
            return self._is_author(user, obj)
        # Если у объекта нет автора, то модификация разрешена только админам
        return False

    def _is_author(self, user: AbstractBaseUser | AnonymousUser | None, obj: "Model") -> bool:
        """
        Проверка, является ли пользователь автором объекта.

        Args:
            user: Пользователь (аутентифицированный, анонимный или None)
            obj: Объект модели

        Returns:
            True если пользователь является автором, False иначе
        """
        # Защита от None и неаутентифицированных пользователей
        if user is None or not user.is_authenticated:
            return False

        # Проверяем наличие поля author
        if hasattr(obj, "author"):
            return obj.author == user

        return False


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permission класс для административных операций.

    Разрешает:
    - Чтение всем
    - Модификацию только staff пользователям
    """

    def has_permission(self, request: Request, view: View) -> bool:  # noqa: ARG002
        """
        Проверка прав доступа к view.

        Args:
            request: HTTP запрос
            view: View, обрабатывающий запрос

        Returns:
            True если доступ разрешен, False иначе
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(isinstance(user, AbstractBaseUser) and user.is_staff)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission класс для объектов с автором.

    Разрешает:
    - Чтение всем
    - Модификацию и удаление только автору объекта
    """

    def has_permission(self, request: Request, view: View) -> bool:  # noqa: ARG002
        """
        Проверка прав доступа на уровне view.

        Args:
            request: HTTP запрос
            view: View, обрабатывающий запрос

        Returns:
            True если доступ разрешен, False иначе
        """
        # Для операций чтения разрешаем доступ всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для операций модификации/удаления требуется аутентификация
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Request, view: View, obj: "Model") -> bool:  # noqa: ARG002
        """
        Проверка прав доступа к конкретному объекту.

        Args:
            request: HTTP запрос
            view: View, обрабатывающий запрос
            obj: Объект модели

        Returns:
            True если доступ разрешен, False иначе
        """
        # Для чтения разрешаем доступ всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для модификации и удаления проверяем авторство
        # Добавляем проверку на None для request.user, чтобы избежать ошибок сравнения
        if hasattr(obj, "author"):
            return request.user is not None and obj.author == request.user

        # Если у объекта нет автора, запрещаем доступ
        return False
