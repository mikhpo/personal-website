'''
Модуль для построения карты сайта по объектам приложения.
'''
from django.contrib.sitemaps import Sitemap
from .models import Article, Series, Topic, Category

class ArticleSitemap(Sitemap):
    protocol = 'https'
    def items(self):
        return Article.objects.filter(public=True)
    def lastmod(self, obj):
        return obj.modified

class SeriesSitemap(Sitemap):
    protocol = 'https'
    def items(self):
        return Series.objects.filter(public=True)

class TopicSitemap(Sitemap):
    protocol = 'https'
    def items(self):
        return Topic.objects.filter(public=True)

class CategorySitemap(Sitemap):
    protocol = 'https'
    def items(self):
        return Category.objects.filter(public=True)