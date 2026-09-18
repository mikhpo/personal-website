"""Модуль для построения карты сайта по объектам приложения Обо мне."""

from django.contrib.sitemaps import Sitemap

from about.models import AboutPage

PROTOCOL = "https"


class AboutSitemap(Sitemap):
    """Карта страницы Обо мне."""

    protocol = PROTOCOL

    def items(self) -> list[AboutPage]:
        """Единственная запись страницы Обо мне."""
        return [AboutPage.get_solo()]

    def location(self, obj: AboutPage) -> str:  # noqa: ARG002
        """Адрес страницы Обо мне одинаков для любой записи."""
        return "/about/"
