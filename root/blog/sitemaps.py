from django.contrib.sitemaps import Sitemap
from blog.models import Article

class ArticleSitemap(Sitemap):
    '''Для построения карты сайта.'''
    protocol = 'https'
    
    def items(self):
        return Article.objects.filter(visible=True)

    def lastmod(self, obj):
        return obj.modified