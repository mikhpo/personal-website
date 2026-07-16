"""Тесты для JWT аутентификации."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class TestJWTAuthentication(APITestCase):
    """Тесты JWT аутентификации."""

    def setUp(self) -> None:
        """Подготовка тестовых данных."""
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_obtain_jwt_token(self) -> None:
        """Тест получения JWT токена."""
        url = reverse("api:token_obtain_pair")
        data = {
            "username": self.username,
            "password": self.password,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_token_with_invalid_credentials(self) -> None:
        """Тест получения токена с неверными данными."""
        url = reverse("api:token_obtain_pair")
        data = {
            "username": self.username,
            "password": "wrongpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_jwt_token(self) -> None:
        """Тест обновления JWT токена."""
        # Получить токены
        obtain_url = reverse("api:token_obtain_pair")
        obtain_data = {
            "username": self.username,
            "password": self.password,
        }
        obtain_response = self.client.post(obtain_url, obtain_data, format="json")
        refresh_token = obtain_response.data["refresh"]

        # Обновить токен
        refresh_url = reverse("api:token_refresh")
        refresh_data = {"refresh": refresh_token}
        refresh_response = self.client.post(refresh_url, refresh_data, format="json")

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

        # При ROTATE_REFRESH_TOKENS=True возвращается новый refresh токен
        self.assertIn("refresh", refresh_response.data)

    def test_verify_jwt_token(self) -> None:
        """Тест верификации JWT токена."""
        # Получить токен
        obtain_url = reverse("api:token_obtain_pair")
        obtain_data = {
            "username": self.username,
            "password": self.password,
        }
        obtain_response = self.client.post(obtain_url, obtain_data, format="json")
        access_token = obtain_response.data["access"]

        # Верифицировать токен
        verify_url = reverse("api:token_verify")
        verify_data = {"token": access_token}
        verify_response = self.client.post(verify_url, verify_data, format="json")
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

    def test_verify_invalid_token(self) -> None:
        """Тест верификации невалидного токена."""
        verify_url = reverse("api:token_verify")
        verify_data = {"token": "invalid_token"}
        verify_response = self.client.post(verify_url, verify_data, format="json")
        self.assertEqual(verify_response.status_code, status.HTTP_401_UNAUTHORIZED)
