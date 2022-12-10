from django.test import TestCase
from blog.models import Article, Series, Topic, Category

class BlogSitemapTest(TestCase):
    '''Тестирование карты блога.'''

    sitemap_url = '/sitemap.xml'

    def test_article_sitemap(self):
        '''Проверяет, что статьи показаны в карте сайта, но только публичные.'''
        public_article = Article.objects.create(title='Public test article', slug='public-test-article', public=True)
        private_artice = Article.objects.create(title='Private test article', slug='private-test-article', public=False)
        response = self.client.get(self.sitemap_url)
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        modified_date = str(public_article.modified.date())
        self.assertTrue('public-test-article' in content)
        self.assertFalse('private-test-article' in content)
        self.assertTrue(modified_date in content)
        
    def test_series_sitemap(self):
        '''Проверяет, что серии добавляются в карту сайта, но только публичные.'''
        Series.objects.create(name='Public test series', slug='public-test-series', public=True)
        Series.objects.create(name='Private test series', slug='private-test-series', public=False)
        response = self.client.get(self.sitemap_url)
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('public-test-series' in content)
        self.assertFalse('private-test-series' in content)

    def test_topic_sitemap(self):
        '''Проверяет, что темы добавляются в карту сайта, но только публичные.'''
        Topic.objects.create(name='Public test topic', slug='public-test-topic', public=True)
        Topic.objects.create(name='Private test topic', slug='private-test-topic', public=False)
        response = self.client.get(self.sitemap_url)
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('public-test-topic' in content)
        self.assertFalse('private-test-topic' in content)

    def test_category_sitemap(self):
        '''Проверяет, что категории добавляются в карту сайта, но только публичные.'''
        Category.objects.create(name='Public test gategory', slug='public-test-gategory', public=True)
        Category.objects.create(name='Private test gategory', slug='private-test-gategory', public=False)
        response = self.client.get(self.sitemap_url)
        self.assertEqual(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('public-test-gategory' in content)
        self.assertFalse('private-test-gategory' in content)
