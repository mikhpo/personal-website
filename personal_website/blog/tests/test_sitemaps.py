"""Тесты карты объектов блога."""

from http import HTTPStatus

from django.test import TestCase
from django.utils import timezone

from blog.factories import ArticleFactory, CategoryFactory, SeriesFactory, TopicFactory


class BlogSitemapTest(TestCase):
    """Тестирование карты блога."""

    sitemap_url = "/sitemap.xml"

    def test_article_sitemap(self) -> None:
        """Проверяет, что статьи показаны в карте сайта, но только публичные."""
        public_article = ArticleFactory(title="Public test article", slug="public-test-article", public=True)
        private_artice = ArticleFactory(title="Private test article", slug="private-test-article", public=False)
        response = self.client.get(self.sitemap_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        local_time = timezone.localtime(public_article.modified_at)
        modified_at_date = str(local_time.date())
        self.assertTrue(public_article.get_absolute_url() in content)
        self.assertFalse(private_artice.get_absolute_url() in content)
        self.assertTrue(modified_at_date in content)

    def test_series_sitemap(self) -> None:
        """Проверяет, что серии добавляются в карту сайта, но только публичные."""
        SeriesFactory(name="Public test series", slug="public-test-series", public=True)
        SeriesFactory(name="Private test series", slug="private-test-series", public=False)
        response = self.client.get(self.sitemap_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        self.assertTrue("public-test-series" in content)
        self.assertFalse("private-test-series" in content)

    def test_topic_sitemap(self) -> None:
        """Проверяет, что темы добавляются в карту сайта, но только публичные."""
        TopicFactory(name="Public test topic", slug="public-test-topic", public=True)
        TopicFactory(name="Private test topic", slug="private-test-topic", public=False)
        response = self.client.get(self.sitemap_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        self.assertTrue("public-test-topic" in content)
        self.assertFalse("private-test-topic" in content)

    def test_category_sitemap(self) -> None:
        """Проверяет, что категории добавляются в карту сайта, но только публичные."""
        CategoryFactory(name="Public test gategory", slug="public-test-gategory", public=True)
        CategoryFactory(name="Private test gategory", slug="private-test-gategory", public=False)
        response = self.client.get(self.sitemap_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        self.assertTrue("public-test-gategory" in content)
        self.assertFalse("private-test-gategory" in content)
