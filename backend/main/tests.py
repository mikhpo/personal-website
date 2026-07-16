"""Тесты главного раздела сайта."""

from http import HTTPStatus

from django.contrib.sitemaps.views import sitemap
from django.test import TestCase
from django.urls import resolve, reverse

from main.views import main


class TestMainPage(TestCase):
    """Тесты загрузки главной страницы сайта."""

    main_url = "/main/"
    reverse_main_url = "main:main"
    template = "main/main.html"
    base_template = "base.html"

    def test_main_page_redirect_url(self) -> None:
        """Тестирование редиректа на главную страницу."""
        response = self.client.get("/")
        self.assertRedirects(response, self.main_url, status_code=301, target_status_code=HTTPStatus.OK)

    def test_main_page_url(self) -> None:
        """Тестирование ссылки на главную страницу."""
        resolver = resolve(self.main_url)
        response = self.client.get(self.main_url)
        self.assertEqual(resolver.func, main)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_main_page_reverse_url(self) -> None:
        """Тестирование именной ссылки на главную страницу."""
        url = reverse(self.reverse_main_url)
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func, main)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_main_page_template(self) -> None:
        """Тестирование загрузки правильного шаблона."""
        response = self.client.get(self.main_url)
        self.assertTemplateUsed(response, self.template)
        self.assertTemplateUsed(response, self.base_template)

    def test_main_page_title(self) -> None:
        """Проверяет, что в заголовке странице указано, что просматривается блог."""
        response = self.client.get(self.main_url)
        self.assertContains(response, "Михаил Поляков")

    def test_main_page_react_component(self) -> None:
        """Проверяет, что на странице присутствует React компонент."""
        response = self.client.get(self.main_url)
        # Проверяем наличие data-component-name для React компонента
        self.assertContains(response, "data-component-name")


class TestSitemap(TestCase):
    """Тестирование карты сайта."""

    def test_sitemap_url(self) -> None:
        """Проверяет доступность карты сайта."""
        sitemap_url = "/sitemap.xml"
        resolver = resolve(sitemap_url)
        response = self.client.get(sitemap_url)
        self.assertEqual(resolver.func, sitemap)
        self.assertEqual(response.status_code, HTTPStatus.OK)
