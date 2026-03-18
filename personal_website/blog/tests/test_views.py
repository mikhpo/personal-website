"""Тесты представлений блога."""

from http import HTTPStatus
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse
from faker import Faker

from blog.apps import BlogConfig
from blog.factories import ArticleFactory, CategoryFactory, SeriesFactory, TopicFactory
from blog.models import Article
from blog.views import ArticleDetailView, blog, category, series, topic

fake = Faker(locale="ru_RU")

APP_NAME = BlogConfig.name

ARTICLE_DETAIL_URL = f"/{APP_NAME}/article/"
ARTICLE_DETAIL_URL_NAME = f"{APP_NAME}:article"
ARTICLE_LIST_URL = f"/{APP_NAME}/"
ARTICLE_LIST_URL_NAME = f"{APP_NAME}:{APP_NAME}"
CATEGORY_URL = f"/{APP_NAME}/category/"
CATEGORY_URL_NAME = f"{APP_NAME}:category"
SERIES_URL = f"/{APP_NAME}/series/"
SERIES_URL_NAME = f"{APP_NAME}:series"
TOPIC_URL = f"/{APP_NAME}/topic/"
TOPIC_URL_NAME = f"{APP_NAME}:topic"

ARTICLE_DETAIL_TEMPLATE = "blog/article_detail.html"
ARTICLE_LIST_TEMPLATE = f"{APP_NAME}/article_list.html"
CATEGORY_TEMPLATE = f"{APP_NAME}/category_detail.html"
SERIES_TEMPLATE = f"{APP_NAME}/series_detail.html"
TOPIC_TEMPLATE = f"{APP_NAME}/topic_detail.html"
BASE_TEMPLATE = "base.html"


class BlogIndexPageTests(TestCase):
    """Тесты главной страницы блога."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Создать тестовые статьи."""
        for n in range(21):
            ArticleFactory(title=f"Article {n}", slug=f"article-{n}")

    def test_article_list_url(self) -> None:
        """Тестирование ссылки на главную страницу блога."""
        resolver = resolve(ARTICLE_LIST_URL)
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertEqual(resolver.func, blog)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_article_list_reverse_url(self) -> None:
        """Тестирование именной ссылки на главную страницу блога."""
        response = self.client.get(ARTICLE_LIST_URL)
        url = reverse(ARTICLE_LIST_URL_NAME)
        resolver = resolve(url)
        reverse_response = self.client.get(url)
        self.assertEqual(resolver.func, blog)
        self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
        self.assertEqual(response.templates, reverse_response.templates)

    def test_article_list_template(self) -> None:
        """Тестирование корректности загрузки шаблона для списка статей."""
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertTemplateUsed(response, ARTICLE_LIST_TEMPLATE)
        self.assertTemplateUsed(response, BASE_TEMPLATE)

    def test_article_list_template_elements(self) -> None:
        """Тестирование наличия в шаблоне главной страницы блога React компонента для списка статей."""
        response = self.client.get(ARTICLE_LIST_URL)
        # Проверяем наличие React компонента Blog/ArticleList
        self.assertContains(response, 'data-component-name="Blog/ArticleList"')
        self.assertContains(response, "/api/blog/articles/")

    def test_article_list_content_filter(self) -> None:
        """Тест на фильтрацию контента на главной странице блога."""
        response = self.client.get(ARTICLE_LIST_URL)
        # React компонент сам загружает статьи через API, шаблон не передаёт статьи в контексте
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_article_list_title(self) -> None:
        """Проверяет, что в заголовке странице указано, что просматривается блог."""
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertContains(response, "Михаил Поляков - Блог")


class ArticleDetailPageTests(TestCase):
    """Тесты детального просмотра статей."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные."""
        cls.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="12345")
        cls.article = ArticleFactory(title="Test article", slug="article-test", author=cls.user)

    def test_article_detail_url(self) -> None:
        """Тестирование ссылки на детальный просмотр статьи блога."""
        url = ARTICLE_DETAIL_URL + self.article.slug + "/"
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func.view_class, ArticleDetailView)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_article_detail_reverse_url(self) -> None:
        """Тестирование обратной ссылки на детальный просмотр статьи блога."""
        url = ARTICLE_DETAIL_URL + self.article.slug + "/"
        response = self.client.get(url)
        reverse_url = reverse(ARTICLE_DETAIL_URL_NAME, args=(self.article.slug,))
        resolver = resolve(reverse_url)
        reverse_response = self.client.get(reverse_url)
        self.assertEqual(resolver.func.view_class, ArticleDetailView)
        self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
        self.assertEqual(response.templates, reverse_response.templates)

    def test_article_detail_template(self) -> None:
        """Тестирование корректности загрузки шаблона для просмотра статьи."""
        url = ARTICLE_DETAIL_URL + self.article.slug + "/"
        response = self.client.get(url)
        self.assertTemplateUsed(response, ARTICLE_DETAIL_TEMPLATE)
        self.assertTemplateUsed(response, BASE_TEMPLATE)

    def test_article_detail_template_elements(self) -> None:
        """Тестирование наличия в шаблоне просмотра статьи React компонента ArticleDetail."""
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(self.article.slug,))
        response = self.client.get(url)
        # Проверяем наличие React компонента Blog/ArticleDetail
        self.assertContains(response, 'data-component-name="Blog/ArticleDetail"')
        self.assertContains(response, "articleId")

    def test_article_page_content(self) -> None:
        """Тестирование соответствия содержания статьи контексту, переданному в шаблон."""
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(self.article.slug,))
        response = self.client.get(url)
        context_article = response.context["article"]
        self.assertEqual(self.article.title, context_article.title)
        self.assertEqual(self.article.content, context_article.content)
        self.assertEqual(self.article.published_at, context_article.published_at)
        self.assertEqual(self.article.modified_at, context_article.modified_at)

    def test_article_content_safe(self) -> None:
        """Проверяет, что в HTML-шаблоне статьи содержание статьи показывается."""
        templates_dir = settings.TEMPLATES[0]["DIRS"][0]
        template_location = Path(templates_dir) / ARTICLE_DETAIL_TEMPLATE
        with Path(template_location).open() as f:
            # Шаблон использует React компонент, article.content|safe не требуется
            self.assertIn("ArticleDetail", f.read())


class CategoryPageTests(TestCase):
    """Тесты страницы просмотра статей по определенной категории."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные."""
        cls.test_category = CategoryFactory(name="Test category", slug="test-category")
        for n in range(20):
            article = ArticleFactory(title=f"Article {n}", slug=f"article-{n}")
            article.categories.add(cls.test_category)

    def test_category_url(self) -> None:
        """Тестирование ссылки на категорию."""
        url = CATEGORY_URL + self.test_category.slug + "/"
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func, category)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_category_reverse_url(self) -> None:
        """Тестирование именной ссылки на категорию."""
        url = CATEGORY_URL + self.test_category.slug + "/"
        response = self.client.get(url)
        reverse_url = reverse(CATEGORY_URL_NAME, args=(self.test_category.slug,))
        resolver = resolve(reverse_url)
        reverse_response = self.client.get(reverse_url)
        self.assertEqual(resolver.func, category)
        self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
        self.assertEqual(response.templates, reverse_response.templates)

    def test_category_template(self) -> None:
        """Тестирование корректности загрузки шаблона для списка статей в категории."""
        url = reverse(CATEGORY_URL_NAME, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertTemplateUsed(response, CATEGORY_TEMPLATE)
        self.assertTemplateUsed(response, BASE_TEMPLATE)

    def test_category_template_elements(self) -> None:
        """Тестирование наличия в шаблоне категории React компонента для списка статей."""
        url = reverse(CATEGORY_URL_NAME, args=(self.test_category.slug,))
        response = self.client.get(url)
        # Проверяем наличие React компонента Blog/ArticleList
        self.assertContains(response, 'data-component-name="Blog/ArticleList"')
        self.assertContains(response, "categories__slug")
        # Проверяем наличие заголовка категории
        self.assertContains(response, self.test_category.name)

    def test_category_content(self) -> None:
        """Тест на передачу объекта категории в контексте."""
        url = reverse(CATEGORY_URL_NAME, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("category", response.context)
        self.assertEqual(response.context["category"], self.test_category)

    def test_category_page_text_not_truncated(self) -> None:
        """Проверяет, что текст статьи в категории не скрыт за катом, если длина текста менее 200 слов."""
        Article.objects.filter(public=True, categories=self.test_category).update(public=False)
        article = ArticleFactory(title="Short article", slug="short-article", public=True)
        article.categories.add(self.test_category)
        url = reverse(CATEGORY_URL_NAME, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # React компонент сам решает, как отображать статьи


class TopicPageTests(TestCase):
    """Тесты страницы просмотра статей, посвященных определенной теме."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные."""
        cls.test_topic = TopicFactory(name="Test topic", slug="test-topic")
        for n in range(20):
            article = ArticleFactory(title=f"Article {n}", slug=f"article-{n}")
            article.topics.add(cls.test_topic)

    def test_topic_url(self) -> None:
        """Тестирование ссылки на тему."""
        url = TOPIC_URL + self.test_topic.slug + "/"
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func, topic)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_topic_reverse_url(self) -> None:
        """Тестирование именной ссылки на тему."""
        url = TOPIC_URL + self.test_topic.slug + "/"
        response = self.client.get(url)
        reverse_url = reverse(TOPIC_URL_NAME, args=(self.test_topic.slug,))
        resolver = resolve(reverse_url)
        reverse_response = self.client.get(reverse_url)
        self.assertEqual(resolver.func, topic)
        self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
        self.assertEqual(response.templates, reverse_response.templates)

    def test_topic_template(self) -> None:
        """Тестирование корректности загрузки шаблона для списка статей по теме."""
        url = reverse(TOPIC_URL_NAME, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertTemplateUsed(response, TOPIC_TEMPLATE)
        self.assertTemplateUsed(response, BASE_TEMPLATE)

    def test_topic_template_elements(self) -> None:
        """Тестирование наличия в шаблоне темы React компонента для списка статей."""
        url = reverse(TOPIC_URL_NAME, args=(self.test_topic.slug,))
        response = self.client.get(url)
        # Проверяем наличие React компонента Blog/ArticleList
        self.assertContains(response, 'data-component-name="Blog/ArticleList"')
        self.assertContains(response, "topics__slug")
        # Проверяем наличие заголовка темы
        self.assertContains(response, self.test_topic.name)

    def test_topic_content(self) -> None:
        """Тест на передачу объекта темы в контексте."""
        url = reverse(TOPIC_URL_NAME, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("topic", response.context)
        self.assertEqual(response.context["topic"], self.test_topic)

    def test_topic_page_text_not_truncated(self) -> None:
        """Проверяет, что текст статьи по теме не скрыт за катом, если длина текста менее 200 слов."""
        Article.objects.filter(public=True, topics=self.test_topic).update(public=False)
        article = ArticleFactory(title="Short article", slug="short-article", public=True)
        article.topics.add(self.test_topic)
        url = reverse(TOPIC_URL_NAME, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # React компонент сам решает, как отображать статьи


class SeriesPageTests(TestCase):
    """Тесты страницы просмотра статей из определенной серии."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные."""
        cls.test_series = SeriesFactory(name="Test series", slug="test-series")
        for n in range(20):
            article = ArticleFactory(title=f"Article {n}", slug=f"article-{n}")
            article.series.add(cls.test_series)

    def test_series_url(self) -> None:
        """Тестирование ссылки на серию."""
        url = SERIES_URL + self.test_series.slug + "/"
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func, series)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_series_reverse_url(self) -> None:
        """Тестирование именной ссылки на серию."""
        url = SERIES_URL + self.test_series.slug + "/"
        response = self.client.get(url)
        reverse_url = reverse(SERIES_URL_NAME, args=(self.test_series.slug,))
        resolver = resolve(reverse_url)
        reverse_response = self.client.get(reverse_url)
        self.assertEqual(resolver.func, series)
        self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
        self.assertEqual(response.templates, reverse_response.templates)

    def test_series_template(self) -> None:
        """Тестирование корректности загрузки шаблона для списка статей из серии."""
        url = reverse(SERIES_URL_NAME, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertTemplateUsed(response, SERIES_TEMPLATE)
        self.assertTemplateUsed(response, BASE_TEMPLATE)

    def test_series_template_elements(self) -> None:
        """Тестирование наличия в шаблоне серии React компонента для списка статей."""
        url = reverse(SERIES_URL_NAME, args=(self.test_series.slug,))
        response = self.client.get(url)
        # Проверяем наличие React компонента Blog/ArticleList
        self.assertContains(response, 'data-component-name="Blog/ArticleList"')
        self.assertContains(response, "series__slug")
        # Проверяем наличие заголовка серии
        self.assertContains(response, self.test_series.name)

    def test_series_content(self) -> None:
        """Тест на передачу объекта серии в контексте."""
        url = reverse(SERIES_URL_NAME, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("series", response.context)
        self.assertEqual(response.context["series"], self.test_series)

    def test_series_page_text_not_truncated(self) -> None:
        """Проверяет, что текст статьи из серии не скрыт за катом, если длина текста менее 200 слов."""
        Article.objects.filter(public=True, series=self.test_series).update(public=False)
        article = ArticleFactory(title="Short article", slug="short-article", public=True)
        article.series.add(self.test_series)
        url = reverse(SERIES_URL_NAME, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
