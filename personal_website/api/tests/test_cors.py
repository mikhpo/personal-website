"""Тесты для CORS конфигурации."""

from django.test import TestCase
from django.urls import reverse


class TestCORSConfiguration(TestCase):
    """Тесты конфигурации CORS."""

    def test_cors_headers_present_on_api_endpoint(self) -> None:
        """Тест наличия CORS заголовков на API эндпоинте."""
        url = reverse("api:token_obtain_pair")
        response = self.client.options(
            url,
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )

        self.assertIn("Access-Control-Allow-Origin", response.headers)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://localhost:3000")

    def test_cors_credentials_allowed(self) -> None:
        """Тест разрешения credentials в CORS."""
        url = reverse("api:token_obtain_pair")
        response = self.client.options(
            url,
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )

        self.assertIn("Access-Control-Allow-Credentials", response.headers)
        self.assertEqual(response.headers["Access-Control-Allow-Credentials"], "true")
