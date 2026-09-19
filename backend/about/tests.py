"""Тесты приложения страницы Обо мне."""

import json
from html import unescape
from html.parser import HTMLParser
from http import HTTPStatus

from django.test import TestCase
from django.urls import resolve, reverse
from rest_framework.test import APITestCase

from about.models import About


class DataPropsParser(HTMLParser):
    """Собиратель значений data-props корневых элементов React по их id."""

    def __init__(self) -> None:
        """Пустой словарь собранных значений."""
        super().__init__()
        self.roots: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:  # noqa: ARG002
        """Сохраняет значение data-props элемента с атрибутом id."""
        attributes = {key: value or "" for key, value in attrs}
        if attributes.get("data-props") and attributes.get("id"):
            self.roots[attributes["id"]] = attributes["data-props"]


class TestAbout(TestCase):
    """Тесты страницы Обо мне."""

    about_url = "/about/"
    reverse_about_url = "about:about"
    template = "about/about.html"
    base_template = "base.html"

    def test_about_page_url(self) -> None:
        """Тестирование ссылки на страницу Обо мне."""
        url = reverse(self.reverse_about_url)
        self.assertEqual(url, self.about_url)
        resolver = resolve(self.about_url)
        self.assertEqual(resolver.view_name, self.reverse_about_url)
        response = self.client.get(self.about_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_template(self) -> None:
        """Тестирование загрузки правильного шаблона."""
        response = self.client.get(self.about_url)
        self.assertTemplateUsed(response, self.template)
        self.assertTemplateUsed(response, self.base_template)

    def test_about_page_heading(self) -> None:
        """Проверяет заголовок первого уровня страницы Обо мне независимо от классов оформления."""
        response = self.client.get(self.about_url)
        self.assertRegex(response.content.decode(), r"<h1[^>]*>\s*Обо мне\s*</h1>")

    def test_about_page_react_component(self) -> None:
        """Проверяет монтирование React компонента страницы и адрес API в пропах."""
        response = self.client.get(self.about_url)
        self.assertContains(response, 'data-component-name="About/AboutPage"')
        self.assertContains(response, '"apiUrl": "/api/about/"')

    def test_about_page_navbar_link(self) -> None:
        """Проверяет пункт Обо мне в данных навигационной панели."""
        response = self.client.get(self.about_url)
        parser = DataPropsParser()
        parser.feed(response.content.decode())
        navbar_data = json.loads(unescape(parser.roots["navbar-root"]))
        self.assertIn(
            {"url": "/about/", "text": "Обо мне", "active": True},
            navbar_data["links"],
        )


class TestAboutAPI(APITestCase):
    """Тесты API страницы Обо мне."""

    about_api_url = "/api/about/"

    def test_get_about_page(self) -> None:
        """Получение содержимого страницы: пустой контент существует после миграции."""
        response = self.client.get(self.about_api_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, {"content": ""})

    def test_get_about_page_with_content(self) -> None:
        """Получение содержимого страницы после заполнения в административном сайте."""
        about_page = About.get_solo()
        about_page.content = "<p>Привет!</p>"
        about_page.save()

        response = self.client.get(self.about_api_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, {"content": "<p>Привет!</p>"})

    def test_post_about_page_not_allowed(self) -> None:
        """Изменение содержимого страницы через API запрещено."""
        response = self.client.post(self.about_api_url, {"content": "<p>Спам</p>"}, format="json")
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)


class TestAboutSitemap(TestCase):
    """Тестирование страницы Обо мне в карте сайта."""

    def test_about_page_in_sitemap(self) -> None:
        """Проверяет наличие страницы Обо мне в карте сайта."""
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "<loc>")
        self.assertContains(response, "/about/")
