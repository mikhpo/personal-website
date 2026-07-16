"""Тесты ViewSet'ов для приложения accounts."""

from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class TestUserViewSet(APITestCase):
    """Тесты UserViewSet."""

    def setUp(self) -> None:
        """Подготовка тестовых данных."""
        self.user_data = {
            "username": "testuser",
            "password": "testpass123",
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_get_users_list(self) -> None:
        """Тест получения списка пользователей."""
        response = self.client.get("/api/accounts/users/")
        self.assertEqual(response.status_code, 200)

    def test_get_user_detail(self) -> None:
        """Тест получения детальной информации о пользователе."""
        response = self.client.get(f"/api/accounts/users/{self.user.pk}/")
        self.assertEqual(response.status_code, 200)

    def test_create_user(self) -> None:
        """Тест создания нового пользователя."""
        new_user_data = {
            "username": "newuser",
            "password": "newpass123",
        }
        response = self.client.post("/api/accounts/users/", new_user_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 2)
