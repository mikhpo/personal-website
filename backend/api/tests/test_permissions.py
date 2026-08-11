"""Тесты для кастомных permissions API."""

from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db.models import Model
from django.http import HttpRequest
from rest_framework.request import Request
from rest_framework.test import APITestCase
from rest_framework.views import View

from api.permissions import IsAuthorOrReadOnly, IsPublicOrAuthor, IsStaffOrReadOnly

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()


class MockRequest(Request):
    """Мock объект для запроса."""

    def __init__(self, user: "AbstractUser | None" = None, method: str = "GET") -> None:
        """Инициализация mock объекта для запроса."""
        self.method = method
        django_request = HttpRequest()
        django_request.method = method
        super().__init__(django_request)
        self.user = user if user is not None else AnonymousUser()


class MockView(View):
    """Mock объект для view."""


class MockModel(Model):
    """Mock модель для тестируемого объекта."""

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return f"MockModel(public={self.public})"

    def __init__(self, public: bool = False, author: "AbstractUser | None" = None) -> None:  # noqa: FBT001, FBT002
        """Инициализация mock модели."""
        self.public = public
        self.author = author


class TestIsPublicOrAuthor(APITestCase):
    """Тесты для permission IsPublicOrAuthor."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.permission = IsPublicOrAuthor()
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.staff_user = User.objects.create_user(
            username="staffuser",
            password="testpass123",
            is_staff=True,
        )
        cls.other_user = User.objects.create_user(username="otheruser", password="testpass123")

    def test_has_object_permission_staff_user(self) -> None:
        """Тест разрешения доступа для staff пользователя."""
        request = MockRequest(user=self.staff_user, method="DELETE")
        view = MockView()
        obj = MockModel(public=False, author=self.other_user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))

    def test_has_permission_safe_methods(self) -> None:
        """Тест разрешения доступа для безопасных методов."""
        request = MockRequest(method="GET")
        view = MockView()
        self.assertTrue(self.permission.has_permission(request, view))

    def test_has_permission_unauthenticated_user_create(self) -> None:
        """Тест запрета создания для неаутентифицированного пользователя."""
        request = MockRequest(user=None, method="POST")
        view = MockView()
        self.assertFalse(self.permission.has_permission(request, view))

    def test_has_permission_authenticated_non_staff_write(self) -> None:
        """Тест запрета write-методов для аутентифицированного не-staff.

        Запись (создание/изменение/удаление) объектов доступна только
        администраторам; Комментарии регулируются отдельным permission.
        """
        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            with self.subTest(method=method):
                request = MockRequest(user=self.user, method=method)
                view = MockView()
                self.assertFalse(self.permission.has_permission(request, view))

    def test_has_permission_staff_write(self) -> None:
        """Тест разрешения write-методов для staff пользователя."""
        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            with self.subTest(method=method):
                request = MockRequest(user=self.staff_user, method=method)
                view = MockView()
                self.assertTrue(self.permission.has_permission(request, view))

    def test_has_object_permission_safe_methods_public_object(self) -> None:
        """Тест разрешения доступа для безопасных методов публичного объекта."""
        request = MockRequest(user=self.other_user, method="GET")
        view = MockView()
        obj = MockModel(public=True, author=self.user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_safe_methods_private_object_owner(self) -> None:
        """Тест разрешения доступа владельцу приватного объекта для безопасных методов."""
        request = MockRequest(user=self.user, method="GET")
        view = MockView()
        obj = MockModel(public=False, author=self.user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_safe_methods_private_object_any_user(self) -> None:
        """Чтение приватного объекта разрешено любому пользователю.

        Безопасные методы (GET/HEAD/OPTIONS) разрешены всегда; видимость
        публичных объектов в списках регулируется на уровне get_queryset() view.
        """
        request = MockRequest(user=self.other_user, method="GET")
        view = MockView()
        obj = MockModel(public=False, author=self.user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_modify_non_owner(self) -> None:
        """Тест запрета модификации объекта не-staff пользователем."""
        request = MockRequest(user=self.other_user, method="PUT")
        view = MockView()
        obj = MockModel(public=False, author=self.user)
        self.assertFalse(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_modify_staff(self) -> None:
        """Тест разрешения модификации объекта staff пользователем."""
        request = MockRequest(user=self.staff_user, method="PUT")
        view = MockView()
        obj = MockModel(public=False, author=self.user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))


class TestIsStaffOrReadOnly(APITestCase):
    """Тесты для permission IsStaffOrReadOnly."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.permission = IsStaffOrReadOnly()
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.staff_user = User.objects.create_user(
            username="staffuser",
            password="testpass123",
            is_staff=True,
        )

    def test_has_permission_safe_methods_unauthenticated(self) -> None:
        """Тест разрешения доступа для безопасных методов неаутентифицированным пользователем."""
        request = MockRequest(user=None, method="GET")
        view = MockView()
        self.assertTrue(self.permission.has_permission(request, view))

    def test_has_permission_safe_methods_authenticated(self) -> None:
        """Тест разрешения доступа для безопасных методов аутентифицированным пользователем."""
        request = MockRequest(user=self.user, method="GET")
        view = MockView()
        self.assertTrue(self.permission.has_permission(request, view))

    def test_has_permission_write_methods_non_staff(self) -> None:
        """Тест запрета доступа для методов записи не-staff пользователем."""
        request = MockRequest(user=self.user, method="POST")
        view = MockView()
        self.assertFalse(self.permission.has_permission(request, view))

    def test_has_permission_write_methods_staff(self) -> None:
        """Тест разрешения доступа для методов записи staff пользователем."""
        request = MockRequest(user=self.staff_user, method="POST")
        view = MockView()
        self.assertTrue(self.permission.has_permission(request, view))


class TestIsAuthorOrReadOnly(APITestCase):
    """Тесты для permission IsAuthorOrReadOnly."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.permission = IsAuthorOrReadOnly()
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.other_user = User.objects.create_user(username="otheruser", password="testpass123")
        cls.staff_user = User.objects.create_user(
            username="staffuser",
            password="testpass123",
            is_staff=True,
        )

    def test_has_object_permission_safe_methods_author(self) -> None:
        """Тест разрешения доступа для безопасных методов автору объекта."""
        request = MockRequest(user=self.user, method="GET")
        view = MockView()
        obj = MockModel(author=self.user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_safe_methods_non_author(self) -> None:
        """Тест разрешения доступа для безопасных методов не-автору объекта."""
        request = MockRequest(user=self.other_user, method="GET")
        view = MockView()
        obj = MockModel(author=self.user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_update_author(self) -> None:
        """Тест разрешения доступа для метода PUT автору объекта."""
        request = MockRequest(user=self.user, method="PUT")
        view = MockView()
        obj = MockModel(author=self.user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_update_non_author(self) -> None:
        """Тест запрета доступа для метода PUT не-автору объекта."""
        request = MockRequest(user=self.other_user, method="PUT")
        view = MockView()
        obj = MockModel(author=self.user)
        self.assertFalse(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_update_staff_non_author(self) -> None:
        """Тест разрешения модификации чужого объекта для staff.

        Администратор может модифицировать любые комментарии, включая чужие.
        """
        request = MockRequest(user=self.staff_user, method="PUT")
        view = MockView()
        obj = MockModel(author=self.user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_delete_author(self) -> None:
        """Тест разрешения доступа для метода DELETE автору объекта."""
        request = MockRequest(user=self.user, method="DELETE")
        view = MockView()
        obj = MockModel(author=self.user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_delete_non_author(self) -> None:
        """Тест запрета доступа для метода DELETE не-автору объекта."""
        request = MockRequest(user=self.other_user, method="DELETE")
        view = MockView()
        obj = MockModel(author=self.user)
        self.assertFalse(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_delete_staff_non_author(self) -> None:
        """Тест разрешения удаления чужого объекта для staff."""
        request = MockRequest(user=self.staff_user, method="DELETE")
        view = MockView()
        obj = MockModel(author=self.user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_modify_none_user(self) -> None:
        """Тест запрета доступа для метода PUT с None пользователем (не должен вызывать ошибку)."""
        request = MockRequest(user=None, method="PUT")
        view = MockView()
        obj = MockModel(author=self.user)
        self.assertFalse(self.permission.has_object_permission(request, view, obj))
