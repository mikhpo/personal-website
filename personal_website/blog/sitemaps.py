"""Модуль для построения карты сайта по объектам блога."""
from datetime import datetime

from django.contrib.sitemaps import Sitemap

from blog.managers import PublicArticleManager, PublicCategoryManager, PublicSeriesManager, PublicTopicManager
from blog.models import Article, Category, Series, Topic

PROTOCOL = "https"


class ArticleSitemap(Sitemap):
    """Карта статей."""

    protocol = PROTOCOL

    def items(self) -> PublicArticleManager:
        """Публичные статьи."""
        return Article.published.all()

    def lastmod(self, obj: Article) -> datetime:
        """Время последнего изменения."""
        return obj.modified_at


class SeriesSitemap(Sitemap):
    """Карта серий статей."""

    protocol = PROTOCOL

    def items(self) -> PublicSeriesManager:
        """Публичные серии."""
        return Series.published.all()


class TopicSitemap(Sitemap):
    """Карта тем статей."""

    protocol = PROTOCOL

    def items(self) -> PublicTopicManager:
        """Публичные темы."""
        return Topic.published.all()


class CategorySitemap(Sitemap):
    """Карта категорий статей."""

    protocol = PROTOCOL

    def items(self) -> PublicCategoryManager:
        """Публичные категории."""
        return Category.published.all()
