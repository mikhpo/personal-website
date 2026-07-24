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
        """Тест запрета доступа для неаутентифицированного пользователя при создании."""
        request = MockRequest(user=None, method="POST")
        view = MockView()
        self.assertFalse(self.permission.has_permission(request, view))

    def test_has_permission_authenticated_user_create(self) -> None:
        """Тест разрешения доступа для аутентифицированного пользователя при создании."""
        request = MockRequest(user=self.user, method="POST")
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

    def test_has_object_permission_safe_methods_private_object_non_owner(self) -> None:
        """Тест запрета доступа к приватному объекту для не-владельца при безопасных методах."""
        request = MockRequest(user=self.other_user, method="GET")
        view = MockView()
        obj = MockModel(public=False, author=self.user)
        self.assertFalse(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_modify_owner(self) -> None:
        """Тест разрешения модификации объекта владельцем."""
        request = MockRequest(user=self.user, method="PUT")
        view = MockView()
        obj = MockModel(public=False, author=self.user)
        self.assertTrue(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_modify_non_owner(self) -> None:
        """Тест запрета модификации объекта не-владельцем."""
        request = MockRequest(user=self.other_user, method="PUT")
        view = MockView()
        obj = MockModel(public=False, author=self.user)
        self.assertFalse(self.permission.has_object_permission(request, view, obj))

    def test_has_object_permission_modify_without_author(self) -> None:
        """Тест запрета модификации объекта без автора."""
        request = MockRequest(user=self.other_user, method="PUT")
        view = MockView()
        obj = MockModel(public=False)  # Нет автора
        self.assertFalse(self.permission.has_object_permission(request, view, obj))

    def test_is_author_with_authenticated_user_and_matching_author(self) -> None:
        """Тест метода _is_author с аутентифицированным пользователем и совпадающим автором."""
        obj = MockModel(author=self.user)
        self.assertTrue(self.permission._is_author(self.user, obj))  # noqa: SLF001

    def test_is_author_with_authenticated_user_and_non_matching_author(self) -> None:
        """Тест метода _is_author с аутентифицированным пользователем и не совпадающим автором."""
        obj = MockModel(author=self.user)
        self.assertFalse(self.permission._is_author(self.other_user, obj))  # noqa: SLF001

    def test_is_author_with_unauthenticated_user(self) -> None:
        """Тест метода _is_author с анонимным (неаутентифицированным) пользователем."""
        obj = MockModel(author=self.user)
        is_author = self.permission._is_author(AnonymousUser(), obj)  # noqa: SLF001
        self.assertFalse(is_author)

    def test_is_author_with_none_user(self) -> None:
        """Тест метода _is_author с None пользователем (не должен вызывать ошибку)."""
        obj = MockModel(author=self.user)
        is_author = self.permission._is_author(None, obj)  # noqa: SLF001
        self.assertFalse(is_author)


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

    def test_has_object_permission_modify_none_user(self) -> None:
        """Тест запрета доступа для метода PUT с None пользователем (не должен вызывать ошибку)."""
        request = MockRequest(user=None, method="PUT")
        view = MockView()
        obj = MockModel(author=self.user)
        self.assertFalse(self.permission.has_object_permission(request, view, obj))
