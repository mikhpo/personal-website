"""Тесты для OpenAPI схемы."""

import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestSchemaGeneration(APITestCase):
    """Тесты генерации OpenAPI схемы."""

    def test_api_root_redirect_to_docs(self) -> None:
        """Тест редиректа с /api/ на /api/docs/."""
        url = reverse("api:api_root")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, "/api/docs/")

    def test_docs_redirect_to_swagger(self) -> None:
        """Тест редиректа с /docs/ на /docs/swagger/."""
        url = reverse("api:docs")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, "/api/docs/swagger/")

    def test_schema_endpoint_returns_openapi_json(self) -> None:
        """Тест доступности эндпоинта схемы и проверка структуры OpenAPI."""
        url = reverse("api:schema")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("application/vnd.oai.openapi", response["Content-Type"])

    def test_schema_contains_jwt_endpoints(self) -> None:
        """Тест наличия JWT эндпоинтов в схеме."""
        url = reverse("api:schema")
        response = self.client.get(url, HTTP_ACCEPT="application/json")

        # Получить схему как JSON
        schema = json.loads(response.content.decode("utf-8"))

        # Проверить наличие путей для JWT
        paths = schema.get("paths", {})
        self.assertIn("/api/auth/token/", paths)
        self.assertIn("/api/auth/token/refresh/", paths)
        self.assertIn("/api/auth/token/verify/", paths)

        # Проверить методы
        self.assertIn("post", paths["/api/auth/token/"])
        self.assertIn("post", paths["/api/auth/token/refresh/"])
        self.assertIn("post", paths["/api/auth/token/verify/"])

    def test_swagger_ui_accessible(self) -> None:
        """Тест доступности Swagger UI."""
        url = reverse("api:swagger")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_redoc_accessible(self) -> None:
        """Тест доступности ReDoc."""
        url = reverse("api:redoc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_swagger_ui_offline_mode(self) -> None:
        """Тест работы Swagger UI в offline режиме (без внешних зависимостей)."""
        url = reverse("api:swagger")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что в ответе нет ссылок на внешние CDN
        content = response.content.decode("utf-8")
        self.assertNotIn("cdn.jsdelivr.net", content)
        self.assertNotIn("unpkg.com", content)

    def test_redoc_offline_mode(self) -> None:
        """Тест работы ReDoc в offline режиме (без внешних зависимостей)."""
        url = reverse("api:redoc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что в ответе нет ссылок на внешние CDN
        content = response.content.decode("utf-8")
        self.assertNotIn("cdn.jsdelivr.net", content)
        self.assertNotIn("unpkg.com", content)
