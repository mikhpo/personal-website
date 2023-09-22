"""
Модуль для построения карты сайта по объектам блога.
"""
from blog.models import Article, Category, Series, Topic
from django.contrib.sitemaps import Sitemap


class ArticleSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Article.published.all()

    def lastmod(self, obj: Article):
        return obj.modified_at


class SeriesSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Series.published.all()


class TopicSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Topic.published.all()


class CategorySitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Category.published.all()
