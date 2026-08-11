"""Кастомные permissions для REST API."""

from typing import TYPE_CHECKING

from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View

if TYPE_CHECKING:
    from django.db.models import Model


class IsPublicOrAuthor(permissions.BasePermission):
    """
    Permission класс для моделей с полем public (gallery: Album, Photo;
    blog: Article, Category, Topic, Series).

    Чтение: безопасные методы разрешены всем. Видимость конкретного объекта
    в списках (list/индекс/sitemap) регулируется на уровне get_queryset()
    соответствующего view — публичными считаются объекты с public=True,
    но детальный просмотр (retrieve/detail) любого объекта по прямой ссылке
    доступен всем пользователям (share-by-link).

    Запись (создание/изменение/удаление) любых объектов — независимо от
    значения public — доступна только администраторам (staff).

    Комментарии к статьям регулируются отдельным permission (см. CommentViewSet
    и IsAuthorOrReadOnly).

    Модель должна иметь поле:
    - public: BooleanField
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

        # Запись (создание/изменение/удаление) — только для администраторов
        user = request.user
        return bool(isinstance(user, AbstractBaseUser) and user.is_staff)

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
        # в списках регулируется на уровне get_queryset() view. Запись для
        # не-staff запрещена (см. has_permission).
        return request.method in permissions.SAFE_METHODS


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
    Permission класс для объектов с автором (используется для комментариев).

    Разрешает:
    - Чтение всем
    - Создание любому аутентифицированному (регулируется has_permission
      и IsAuthenticatedOrReadOnly в CommentViewSet)
    - Модификацию и удаление автору объекта или администратору (staff)
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
            view: View, обрабатывающая запрос
            obj: Объект модели

        Returns:
            True если доступ разрешен, False иначе
        """
        # Для чтения разрешаем доступ всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Администраторы могут модифицировать и удалять любые объекты
        user = request.user
        if isinstance(user, AbstractBaseUser) and user.is_staff:
            return True

        # Для модификации и удаления проверяем авторство
        if hasattr(obj, "author"):
            return user is not None and obj.author == user

        # Если у объекта нет автора, запрещаем доступ
        return False
