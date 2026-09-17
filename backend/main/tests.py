"""Тесты главного раздела сайта."""

from http import HTTPStatus

from django.contrib.sitemaps.views import sitemap
from django.test import TestCase
from django.urls import resolve, reverse
from rest_framework.test import APITestCase

from main.models import AboutPage
from main.views import main, search


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

    def test_main_page_theme(self) -> None:
        """Проверяет, что страница по умолчанию отрисовывается в светлой теме."""
        response = self.client.get(self.main_url)
        self.assertContains(response, 'data-bs-theme="light"')


class TestSearchPage(TestCase):
    """Тесты страницы общего поиска по сайту."""

    search_url = "/main/search/"
    template = "main/search.html"
    base_template = "base.html"

    def test_search_page_url(self) -> None:
        """Тестирование ссылки на страницу общего поиска."""
        resolver = resolve(self.search_url)
        response = self.client.get(self.search_url)
        self.assertEqual(resolver.func, search)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_search_page_template(self) -> None:
        """Тестирование загрузки правильного шаблона."""
        response = self.client.get(self.search_url)
        self.assertTemplateUsed(response, self.template)
        self.assertTemplateUsed(response, self.base_template)

    def test_search_page_components(self) -> None:
        """Проверяет монтирование формы поиска и компонента результатов."""
        response = self.client.get(self.search_url)
        self.assertContains(response, 'data-component-name="Search/SearchForm"')
        self.assertContains(response, '"targetUrl": "/main/search/"')
        self.assertContains(response, 'data-component-name="Search/SearchResults"')

    def test_search_page_search_parameter(self) -> None:
        """Тестирование передачи поискового запроса в React компоненты страницы."""
        response = self.client.get(self.search_url, {"search": "react"})

        # Поисковый запрос попадает в пропы SearchForm и SearchResults
        self.assertContains(response, '"search": "react"')


class TestSitemap(TestCase):
    """Тестирование карты сайта."""

    def test_sitemap_url(self) -> None:
        """Проверяет доступность карты сайта."""
        sitemap_url = "/sitemap.xml"
        resolver = resolve(sitemap_url)
        response = self.client.get(sitemap_url)
        self.assertEqual(resolver.func, sitemap)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestAboutPage(TestCase):
    """Тесты страницы Обо мне."""

    about_url = "/about/"
    reverse_about_url = "about"
    template = "main/about.html"
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
        """Проверяет заголовок страницы Обо мне."""
        response = self.client.get(self.about_url)
        self.assertContains(response, '<h1 class="mb-3">Обо мне</h1>')

    def test_about_page_react_component(self) -> None:
        """Проверяет монтирование React компонента страницы и адрес API в пропах."""
        response = self.client.get(self.about_url)
        self.assertContains(response, 'data-component-name="Main/AboutPage"')
        self.assertContains(response, '"apiUrl": "/api/main/about/"')

    def test_about_page_navbar_link(self) -> None:
        """Проверяет пункт Обо мне в навигационной панели."""
        response = self.client.get(self.about_url)
        # Кириллица в data-props экранируется json.dumps в \uXXXX,
        # а кавычки - html.escape в &quot;
        navbar_link = (
            "&quot;url&quot;: &quot;/about/&quot;, "
            "&quot;text&quot;: &quot;\\u041e\\u0431\\u043e \\u043c\\u043d\\u0435&quot;"
        )
        self.assertContains(response, navbar_link)


class TestAboutAPI(APITestCase):
    """Тесты API страницы Обо мне."""

    about_api_url = "/api/main/about/"

    def test_get_about_page(self) -> None:
        """Получение содержимого страницы: пустой контент существует после миграции."""
        response = self.client.get(self.about_api_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, {"content": ""})

    def test_get_about_page_with_content(self) -> None:
        """Получение содержимого страницы после заполнения в административном сайте."""
        about_page = AboutPage.get_solo()
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
