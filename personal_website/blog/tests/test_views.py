"""Тесты представлений блога."""

from http import HTTPStatus
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse
from faker import Faker

from blog.apps import BlogConfig
from blog.factories import ArticleFactory, CategoryFactory, CommentFactory, SeriesFactory, TopicFactory
from blog.models import Article, Comment
from blog.views import ArticleDetailView, blog, category, series, topic
from personal_website.utils import generate_random_text

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
CATEGORY_TEMPLATE = f"{APP_NAME}/article_list.html"
SERIES_TEMPLATE = f"{APP_NAME}/article_list.html"
TOPIC_TEMPLATE = f"{APP_NAME}/article_list.html"
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
        """Тестирование наличия в шаблоне главной страницы блога HTML-элементов для карточки статьи и паджинации."""
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertContains(response, 'class="card-body"')
        self.assertContains(response, 'class="card-title"')
        self.assertContains(response, 'class="card-text"')
        self.assertContains(response, 'class="pagination"')

    def test_article_list_pagination(self) -> None:
        """Проверка на корректность паджинации статей блога на главной странице блога."""
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertTrue("page_obj" in response.context)
        self.assertLessEqual(len(response.context["page_obj"]), 5)

    def test_article_list_content_filter(self) -> None:
        """Тест на фильтрацию контента на главной странице блога."""
        response = self.client.get(ARTICLE_LIST_URL)
        page_articles: list[Article] = response.context["page_obj"]
        for article in page_articles:
            self.assertTrue(article.public)

    def test_article_list_text_truncated(self) -> None:
        """Проверяет, что текст статьи скрыт за катом, если длина текста более 200 слов."""
        Article.objects.filter(public=True).update(public=False)
        ArticleFactory(title="Long article", slug="long-article", public=True, content=generate_random_text(201))
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, ">Читать дальше<")

    def test_article_list_text_not_truncated(self) -> None:
        """Проверяет, что текст статьи не скрыт за катом, если длина текста менее 200 слов."""
        Article.objects.filter(public=True).update(public=False)
        ArticleFactory(title="Short article", slug="short-article", public=True)
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotContains(response, ">Читать дальше<")

    def test_article_list_content_safe(self) -> None:
        """Проверяет, что в HTML-шаблоне блога содержание статей показывается без HTML-разметки."""
        templates_dir = settings.TEMPLATES[0]["DIRS"][0]
        template_location = Path(templates_dir) / ARTICLE_LIST_TEMPLATE
        with Path(template_location).open() as f:
            self.assertIn("article.content|safe", f.read())

    def test_article_list_article_order(self) -> None:
        """Проверяет, что статьи на главной странице блога отсортированы в правильном порядке."""
        response = self.client.get(ARTICLE_LIST_URL)
        target_articles = Article.objects.filter(public=True).order_by("-published_at")[:5]
        response_articles = response.context["page_obj"]
        self.assertQuerySetEqual(target_articles, response_articles)

    def test_article_list_title(self) -> None:
        """Проверяет, что в заголовке странице указано, что просматривается блог."""
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertContains(response, "Михаил Поляков - Блог")


class ArticleDetailPageTests(TestCase):
    """Тесты детального просмотра статей."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные."""
        User.objects.create_user(username="testuser", email="testuser@example.com", password="12345")
        ArticleFactory(title="Test article", slug="article-test")

    def test_article_detail_url(self) -> None:
        """Тестирование ссылки на детальный просмотр статьи блога."""
        article = Article.objects.get(title="Test article")
        url = ARTICLE_DETAIL_URL + article.slug + "/"
        resolver = resolve(url)
        response = self.client.get(url)
        self.assertEqual(resolver.func.view_class, ArticleDetailView)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_article_detail_reverse_url(self) -> None:
        """Тестирование обратной ссылки на детальный просмотр статьи блога."""
        article = Article.objects.get(title="Test article")
        url = ARTICLE_DETAIL_URL + article.slug + "/"
        response = self.client.get(url)
        reverse_url = reverse(ARTICLE_DETAIL_URL_NAME, args=(article.slug,))
        resolver = resolve(reverse_url)
        reverse_response = self.client.get(reverse_url)
        self.assertEqual(resolver.func.view_class, ArticleDetailView)
        self.assertEqual(reverse_response.status_code, HTTPStatus.OK)
        self.assertEqual(response.templates, reverse_response.templates)

    def test_article_detail_template(self) -> None:
        """Тестирование корректности загрузки шаблона для просмотра статьи."""
        article = Article.objects.get(title="Test article")
        url = ARTICLE_DETAIL_URL + article.slug + "/"
        response = self.client.get(url)
        self.assertTemplateUsed(response, ARTICLE_DETAIL_TEMPLATE)
        self.assertTemplateUsed(response, BASE_TEMPLATE)

    def test_article_detail_template_elements(self) -> None:
        """Тестирование наличия в шаблоне просмотра статьи HTML-элементов для атрибутов статьи и паджинации."""
        article = Article.objects.get(title="Test article")
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(article.slug,))
        response = self.client.get(url)
        self.assertContains(response, 'class="card-body"')
        self.assertContains(response, 'class="card-title"')
        self.assertContains(response, 'class="card-text"')
        self.assertContains(response, 'class="card-footer"')
        self.assertContains(response, 'id="comments_section"')

    def test_article_page_content(self) -> None:
        """Тестирование соответствия содержания статьи контексту, переданному в шаблон."""
        article = Article.objects.get(title="Test article")
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(article.slug,))
        response = self.client.get(url)
        context: Article = response.context["article"]
        self.assertEqual(article.title, context.title)
        self.assertEqual(article.content, context.content)
        self.assertEqual(article.published_at, context.published_at)
        self.assertEqual(article.modified_at, context.modified_at)

    def test_article_comment_button_access(self) -> None:
        """Тестирование добавления и вывода комментариев к статьям в блоге."""
        article = Article.objects.get(title="Test article")
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(article.slug,))
        self.assertFalse(get_user(self.client).is_authenticated)
        response = self.client.get(url)
        self.assertNotContains(response, "Добавить комментарий")
        self.client.login(username="testuser", password="12345")
        self.assertTrue(get_user(self.client).is_authenticated)
        response = self.client.get(url)
        self.assertContains(response, "Добавить комментарий")

    def test_comments_post(self) -> None:
        """Проверка на обязательность авторизации перед созданием комментария."""
        article = Article.objects.get(title="Test article")
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(article.slug,))
        with self.assertRaises(ValueError):
            response = self.client.post(url, data={"content": "test comment"})
        self.client.login(username="testuser", password="12345")
        response = self.client.post(url, data={"content": "test comment"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Comment.objects.filter(content="test comment").exists())

    def test_comments_logging(self) -> None:
        """Проверка на запись в лог факта создания нового комментария."""
        article = Article.objects.get(title="Test article")
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(article.slug,))
        self.client.login(username="testuser", password="12345")
        with self.assertLogs(logger=settings.PROJECT_NAME, level="INFO") as cm:
            response = self.client.post(url, data={"content": "test comment"})
            user = response.context["user"]
            self.assertIn(
                f"INFO:{settings.PROJECT_NAME}:Пользователь {user} оставил комментарий к статье {article}",
                cm.output,
            )

    def test_comments_ordered_by_posted(self) -> None:
        """Проверка порядка показа комментариев."""
        article = Article.objects.get(title="Test article")
        user = User.objects.get(username="testuser")
        for i in range(1, 6):
            CommentFactory(article=article, author=user, content=f"test comment {i}")
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(article.slug,))
        response = self.client.get(url)
        target_comments = Comment.objects.filter(article=article).order_by("posted")
        response_comments = response.context["comments"]
        self.assertQuerySetEqual(target_comments, response_comments)
        self.assertEqual(response_comments[0].content, "test comment 1")

    def test_article_content_safe(self) -> None:
        """Проверяет, что в HTML-шаблоне статьи содержание статьи показывается."""
        templates_dir = settings.TEMPLATES[0]["DIRS"][0]
        template_location = Path(templates_dir) / ARTICLE_DETAIL_TEMPLATE
        with Path(template_location).open() as f:
            self.assertIn("article.content|safe", f.read())


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
        """Тестирование наличия в шаблоне категории HTML-элементов для карточки статьи и паджинации."""
        url = reverse(CATEGORY_URL_NAME, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertContains(response, 'class="card-body"')
        self.assertContains(response, 'class="card-title"')
        self.assertContains(response, 'class="card-text"')
        self.assertContains(response, 'class="pagination"')

    def test_category_pagination(self) -> None:
        """Проверка на корректность паджинации статей в категории."""
        url = reverse(CATEGORY_URL_NAME, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertTrue("page_obj" in response.context)
        self.assertLessEqual(len(response.context["page_obj"]), 5)

    def test_category_content_filter(self) -> None:
        """Тест на фильтрацию контента на странице просмотра категории."""
        url = reverse(CATEGORY_URL_NAME, args=(self.test_category.slug,))
        response = self.client.get(url)
        page_articles: list[Article] = response.context["page_obj"]
        for article in page_articles:
            self.assertTrue(article.public)

    def test_category_page_text_truncated(self) -> None:
        """Проверяет, что текст статьи в категории скрыт за катом, если длина текста более 200 слов."""
        Article.objects.filter(public=True, categories=self.test_category).update(public=False)
        article = ArticleFactory(
            title="Long article",
            slug="long-article",
            public=True,
            content=generate_random_text(201),
        )
        article.categories.add(self.test_category)
        url = reverse(CATEGORY_URL_NAME, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, ">Читать дальше<")

    def test_category_page_text_not_truncated(self) -> None:
        """Проверяет, что текст статьи в категории не скрыт за катом, если длина текста менее 200 слов."""
        Article.objects.filter(public=True, categories=self.test_category).update(public=False)
        article = ArticleFactory(title="Short article", slug="short-article", public=True)
        article.categories.add(self.test_category)
        url = reverse(CATEGORY_URL_NAME, args=(self.test_category.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotContains(response, ">Читать дальше<")

    def test_category_content_safe(self) -> None:
        """Проверяет, что в HTML-шаблоне списка статей в категории содержание статей показывается без HTML-разметки."""
        templates_dir = settings.TEMPLATES[0]["DIRS"][0]
        template_location = Path(templates_dir) / CATEGORY_TEMPLATE
        with Path(template_location).open() as f:
            self.assertIn("article.content|safe", f.read())

    def test_category_article_order(self) -> None:
        """Проверяет, что статьи в категории отсортированы в правильном порядке."""
        url = reverse(CATEGORY_URL_NAME, args=(self.test_category.slug,))
        response = self.client.get(url)
        target_articles = Article.objects.filter(public=True, categories=self.test_category).order_by("-published_at")[
            :5
        ]
        response_articles = response.context["page_obj"]
        self.assertQuerySetEqual(target_articles, response_articles)


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
        """Тестирование наличия в шаблоне темы HTML-элементов для карточки статьи и паджинации."""
        url = reverse(TOPIC_URL_NAME, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertContains(response, 'class="card-body"')
        self.assertContains(response, 'class="card-title"')
        self.assertContains(response, 'class="card-text"')
        self.assertContains(response, 'class="pagination"')

    def test_topic_pagination(self) -> None:
        """Проверка на корректность паджинации статей по теме."""
        url = reverse(TOPIC_URL_NAME, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertTrue("page_obj" in response.context)
        self.assertLessEqual(len(response.context["page_obj"]), 5)

    def test_topic_content_filter(self) -> None:
        """Тест на фильтрацию контента на странице просмотра темы."""
        url = reverse(TOPIC_URL_NAME, args=(self.test_topic.slug,))
        response = self.client.get(url)
        page_articles: list[Article] = response.context["page_obj"]
        for article in page_articles:
            self.assertTrue(article.public)

    def test_topic_page_text_truncated(self) -> None:
        """Проверяет, что текст статьи по теме скрыт за катом, если длина текста более 200 слов."""
        Article.objects.filter(public=True, topics=self.test_topic).update(public=False)
        article = ArticleFactory(
            title="Long article",
            slug="long-article",
            public=True,
            content=generate_random_text(201),
        )
        article.topics.add(self.test_topic)
        url = reverse(TOPIC_URL_NAME, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, ">Читать дальше<")

    def test_topic_page_text_not_truncated(self) -> None:
        """Проверяет, что текст статьи по теме не скрыт за катом, если длина текста менее 200 слов."""
        Article.objects.filter(public=True, topics=self.test_topic).update(public=False)
        article = ArticleFactory(title="Short article", slug="short-article", public=True)
        article.topics.add(self.test_topic)
        url = reverse(TOPIC_URL_NAME, args=(self.test_topic.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotContains(response, ">Читать дальше<")

    def test_topic_content_safe(self) -> None:
        """Проверяет, что в HTML-шаблоне списка статей по теме содержание статей показывается без HTML-разметки."""
        templates_dir = settings.TEMPLATES[0]["DIRS"][0]
        template_location = Path(templates_dir) / TOPIC_TEMPLATE
        with Path(template_location).open() as f:
            self.assertIn("article.content|safe", f.read())

    def test_topic_article_order(self) -> None:
        """Проверяет, что статьи по теме отсортированы в правильном порядке."""
        url = reverse(TOPIC_URL_NAME, args=(self.test_topic.slug,))
        response = self.client.get(url)
        target_articles = Article.objects.filter(public=True, topics=self.test_topic).order_by("-published_at")[:5]
        response_articles = response.context["page_obj"]
        self.assertQuerySetEqual(target_articles, response_articles)


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
        """Тестирование наличия в шаблоне серии HTML-элементов для карточки статьи и паджинации."""
        url = reverse(SERIES_URL_NAME, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertContains(response, 'class="card-body"')
        self.assertContains(response, 'class="card-title"')
        self.assertContains(response, 'class="card-text"')
        self.assertContains(response, 'class="pagination"')

    def test_series_pagination(self) -> None:
        """Проверка на корректность паджинации статей из серии."""
        url = reverse(SERIES_URL_NAME, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertTrue("page_obj" in response.context)
        self.assertLessEqual(len(response.context["page_obj"]), 5)

    def test_series_content_filter(self) -> None:
        """Тест на фильтрацию контента на странице просмотра серии."""
        url = reverse(SERIES_URL_NAME, args=(self.test_series.slug,))
        response = self.client.get(url)
        page_articles: list[Article] = response.context["page_obj"]
        for article in page_articles:
            self.assertTrue(article.public)

    def test_series_page_text_truncated(self) -> None:
        """Проверяет, что текст статьи из серии скрыт за катом, если длина текста более 200 слов."""
        Article.objects.filter(public=True, series=self.test_series).update(public=False)
        article = ArticleFactory(
            title="Long article",
            slug="long-article",
            public=True,
            content=generate_random_text(201),
        )
        article.series.add(self.test_series)
        url = reverse(SERIES_URL_NAME, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, ">Читать дальше<")

    def test_series_page_text_not_truncated(self) -> None:
        """Проверяет, что текст статьи из серии не скрыт за катом, если длина текста менее 200 слов."""
        Article.objects.filter(public=True, series=self.test_series).update(public=False)
        article = ArticleFactory(title="Short article", slug="short-article", public=True)
        article.series.add(self.test_series)
        url = reverse(SERIES_URL_NAME, args=(self.test_series.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotContains(response, ">Читать дальше<")

    def test_series_content_safe(self) -> None:
        """Проверяет, что в HTML-шаблоне списка статей из серии содержание статей показывается без HTML-разметки."""
        templates_dir = settings.TEMPLATES[0]["DIRS"][0]
        template_location = Path(templates_dir) / SERIES_TEMPLATE
        with Path(template_location).open() as f:
            self.assertIn("article.content|safe", f.read())

    def test_series_article_order(self) -> None:
        """Проверяет, что статьи из серии отсортированы в правильном порядке."""
        url = reverse(SERIES_URL_NAME, args=(self.test_series.slug,))
        response = self.client.get(url)
        target_articles = Article.objects.filter(public=True, series=self.test_series).order_by("-published_at")[:5]
        response_articles = response.context["page_obj"]
        self.assertQuerySetEqual(target_articles, response_articles)
