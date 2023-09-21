from http import HTTPStatus

from django.test import TestCase
from django.utils import timezone

from blog.models import Article, Category, Series, Topic


class BlogSitemapTest(TestCase):
    """
    Тестирование карты блога.
    """

    SITEMAP_URL = "/sitemap.xml"

    def test_article_sitemap(self):
        """
        Проверяет, что статьи показаны в карте сайта, но только публичные.
        """
        public_article = Article.objects.create(
            title="Public test article", slug="public-test-article", public=True
        )
        private_artice = Article.objects.create(
            title="Private test article", slug="private-test-article", public=False
        )
        response = self.client.get(self.SITEMAP_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        local_time = timezone.localtime(public_article.modified_at)
        modified_at_date = str(local_time.date())
        self.assertTrue(public_article.get_absolute_url() in content)
        self.assertFalse(private_artice.get_absolute_url() in content)
        self.assertTrue(modified_at_date in content)

    def test_series_sitemap(self):
        """
        Проверяет, что серии добавляются в карту сайта, но только публичные.
        """
        Series.objects.create(
            name="Public test series", slug="public-test-series", public=True
        )
        Series.objects.create(
            name="Private test series", slug="private-test-series", public=False
        )
        response = self.client.get(self.SITEMAP_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        self.assertTrue("public-test-series" in content)
        self.assertFalse("private-test-series" in content)

    def test_topic_sitemap(self):
        """
        Проверяет, что темы добавляются в карту сайта, но только публичные.
        """
        Topic.objects.create(
            name="Public test topic", slug="public-test-topic", public=True
        )
        Topic.objects.create(
            name="Private test topic", slug="private-test-topic", public=False
        )
        response = self.client.get(self.SITEMAP_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        self.assertTrue("public-test-topic" in content)
        self.assertFalse("private-test-topic" in content)

    def test_category_sitemap(self):
        """
        Проверяет, что категории добавляются в карту сайта, но только публичные.
        """
        Category.objects.create(
            name="Public test gategory", slug="public-test-gategory", public=True
        )
        Category.objects.create(
            name="Private test gategory", slug="private-test-gategory", public=False
        )
        response = self.client.get(self.SITEMAP_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        self.assertTrue("public-test-gategory" in content)
        self.assertFalse("private-test-gategory" in content)
