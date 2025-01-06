"""Модуль для построения карты сайта по объектам блога."""

from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.db.models import QuerySet

from blog.models import Article, Category, Series, Topic

PROTOCOL = "https"


class ArticleSitemap(Sitemap):
    """Карта статей."""

    protocol = PROTOCOL

    def items(self) -> QuerySet[Article]:
        """Публичные статьи."""
        return Article.published.all()

    def lastmod(self, obj: Article) -> datetime:
        """Время последнего изменения."""
        return obj.modified_at


class SeriesSitemap(Sitemap):
    """Карта серий статей."""

    protocol = PROTOCOL

    def items(self) -> QuerySet[Series]:
        """Публичные серии."""
        return Series.published.all()


class TopicSitemap(Sitemap):
    """Карта тем статей."""

    protocol = PROTOCOL

    def items(self) -> QuerySet[Topic]:
        """Публичные темы."""
        return Topic.published.all()


class CategorySitemap(Sitemap):
    """Карта категорий статей."""

    protocol = PROTOCOL

    def items(self) -> QuerySet[Category]:
        """Публичные категории."""
        return Category.published.all()
