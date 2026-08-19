"""Тесты представлений основного модуля проекта."""

from http import HTTPStatus
from unittest.mock import patch

from django.db.utils import OperationalError
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from personal_website.views import StaticRedirectView

S3_STATIC_URL = "https://storage.yandexcloud.net/personal-website-storage/static/"


class TestStaticRedirectView(SimpleTestCase):
    """Тесты постоянных редиректов на статические файлы."""

    def test_favicon_returns_permanent_redirect(self) -> None:
        """Запрос фавикона выполняет постоянный редирект."""
        response = self.client.get("/favicon.ico")
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)
        self.assertTrue(response["Location"].endswith("favicon.ico"))

    def test_robots_returns_permanent_redirect(self) -> None:
        """Запрос robots.txt выполняет постоянный редирект."""
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)
        self.assertTrue(response["Location"].endswith("robots.txt"))

    @override_settings(STATIC_URL=S3_STATIC_URL)
    def test_redirect_targets_s3_bucket_in_s3_mode(self) -> None:
        """В S3-режиме цель редиректа указывает в бакет объектного хранилища."""
        response = self.client.get("/favicon.ico")
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)
        self.assertEqual(response["Location"], f"{S3_STATIC_URL}favicon.ico")

    def test_urls_are_resolvable(self) -> None:
        """Маршруты резолвятся в представления редиректа."""
        for name, path in (("favicon", "/favicon.ico"), ("robots", "/robots.txt")):
            with self.subTest(name=name):
                self.assertEqual(reverse(name), path)
                resolver_match = self.client.get(path).resolver_match
                self.assertIsNotNone(resolver_match)
                self.assertEqual(resolver_match.url_name, name)
                self.assertEqual(resolver_match.func.view_class, StaticRedirectView)


class TestHealthView(TestCase):
    """Тесты эндпоинта проверки живости приложения и базы данных."""

    def test_health_returns_ok_with_available_database(self) -> None:
        """При доступной базе данных эндпоинт отвечает статусом 200 и телом ok."""
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.content, b"ok")

    def test_health_returns_service_unavailable_on_database_error(self) -> None:
        """При ошибке обращения к базе данных эндпоинт отвечает статусом 503."""
        with patch("personal_website.views.connection.cursor") as mock_cursor:
            mock_cursor.side_effect = OperationalError
            response = self.client.get("/health/")
        self.assertEqual(response.status_code, HTTPStatus.SERVICE_UNAVAILABLE)
