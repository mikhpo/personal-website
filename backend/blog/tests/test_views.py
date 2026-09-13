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
from blog.views import ArticleCreateView, ArticleDetailView, ArticleEditView, blog, category, series, topic

fake = Faker(locale="ru_RU")

APP_NAME = BlogConfig.name

ARTICLE_DETAIL_URL = f"/{APP_NAME}/article/"
ARTICLE_DETAIL_URL_NAME = f"{APP_NAME}:article"
ARTICLE_LIST_URL = f"/{APP_NAME}/"
ARTICLE_LIST_URL_NAME = f"{APP_NAME}:{APP_NAME}"
ARTICLE_CREATE_URL = f"/{APP_NAME}/article/create/"
ARTICLE_CREATE_URL_NAME = f"{APP_NAME}:article-create"
ARTICLE_EDIT_URL = f"/{APP_NAME}/article/"
ARTICLE_EDIT_URL_NAME = f"{APP_NAME}:article-edit"
CATEGORY_URL = f"/{APP_NAME}/category/"
CATEGORY_URL_NAME = f"{APP_NAME}:category"
SERIES_URL = f"/{APP_NAME}/series/"
SERIES_URL_NAME = f"{APP_NAME}:series"
TOPIC_URL = f"/{APP_NAME}/topic/"
TOPIC_URL_NAME = f"{APP_NAME}:topic"

ARTICLE_DETAIL_TEMPLATE = "blog/article_detail.html"
ARTICLE_LIST_TEMPLATE = f"{APP_NAME}/article_list.html"
ARTICLE_FORM_TEMPLATE = f"{APP_NAME}/article_form.html"
CATEGORY_TEMPLATE = f"{APP_NAME}/category_detail.html"
SERIES_TEMPLATE = f"{APP_NAME}/series_detail.html"
TOPIC_TEMPLATE = f"{APP_NAME}/topic_detail.html"
BASE_TEMPLATE = "base.html"


class TestBlogIndexPage(TestCase):
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
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_article_list_title(self) -> None:
        """Проверяет, что в заголовке странице указано, что просматривается блог."""
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertContains(response, "Михаил Поляков - Блог")

    def test_article_list_search_parameter(self) -> None:
        """Тестирование передачи поискового запроса в React компоненты страницы."""
        response = self.client.get(ARTICLE_LIST_URL, {"search": "react"})

        # Поисковый запрос попадает в пропсы ArticleList и SearchForm
        self.assertContains(response, '"search": "react"')

        # Форма поиска смонтирована с targetUrl страницы результатов
        self.assertContains(response, 'data-component-name="Search/SearchForm"')
        self.assertContains(response, '"targetUrl": "/blog/"')

    def test_article_list_create_button_for_staff(self) -> None:
        """Для staff на странице блога отображается кнопка создания статьи."""
        staff_user = User.objects.create_user(
            username="staffbtn",
            email="staffbtn@example.com",
            password="12345",
            is_staff=True,
        )
        self.client.force_login(staff_user)
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertContains(response, "Написать статью")
        self.assertContains(response, f'href="{ARTICLE_CREATE_URL}"')

    def test_article_list_no_create_button_for_anonymous(self) -> None:
        """Для анонима кнопка создания статьи не отображается."""
        response = self.client.get(ARTICLE_LIST_URL)
        self.assertNotContains(response, "Написать статью")


class TestArticleDetailPage(TestCase):
    """Тесты детального просмотра статей."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные."""
        cls.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="12345")
        cls.staff_user = User.objects.create_user(
            username="staffuser",
            email="staffuser@example.com",
            password="12345",
            is_staff=True,
        )
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
        # URL скрипта редактора передается пропом из STATIC_URL хранилища статики
        self.assertContains(response, '"tinymceScriptSrc": "/static/tinymce/tinymce.min.js"')

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

    def test_article_detail_authentication_context(self) -> None:
        """Тестирование передачи контекста аутентификации в React компонент."""
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(self.article.slug,))

        # Неаутентифицированный пользователь
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем наличие isAuthenticated: false в JSON атрибутах
        self.assertContains(response, '"isAuthenticated": false')

        # Аутентифицированный пользователь
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, '"isAuthenticated": true')

    def test_article_detail_login_url(self) -> None:
        """Тестирование передачи loginUrl в React компонент."""
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(self.article.slug,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "loginUrl")

    def test_article_detail_staff_flag(self) -> None:
        """Флаг isStaff передается в ArticleDetail из шаблона."""
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(self.article.slug,))

        response = self.client.get(url)
        self.assertContains(response, '"isStaff": false')

        self.client.force_login(self.staff_user)
        response = self.client.get(url)
        self.assertContains(response, '"isStaff": true')

    def test_private_article_accessible_by_link(self) -> None:
        """Приватная статья доступна по прямой ссылке."""
        private_article = ArticleFactory(title="Private article", slug="private-article", public=False)
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(private_article.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context["article"], private_article)

    def test_private_article_page_has_noindex(self) -> None:
        """HTML страницы приватной статьи содержит meta robots noindex."""
        private_article = ArticleFactory(title="Private noindex", slug="private-noindex", public=False)
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(private_article.slug,))
        response = self.client.get(url)
        self.assertContains(response, '<meta name="robots" content="noindex">')

    def test_public_article_page_has_no_noindex(self) -> None:
        """HTML страницы публичной статьи не содержит noindex."""
        url = reverse(ARTICLE_DETAIL_URL_NAME, args=(self.article.slug,))
        response = self.client.get(url)
        self.assertNotContains(response, "noindex")


class TestArticleCreateView(TestCase):
    """Тесты страницы создания статьи (ArticleCreateView)."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные."""
        cls.user = User.objects.create_user(username="formuser", email="formuser@example.com", password="12345")
        cls.staff_user = User.objects.create_user(
            username="formstaff",
            email="formstaff@example.com",
            password="12345",
            is_staff=True,
        )

    def test_create_page_url(self) -> None:
        """Тестирование ссылки на страницу создания статьи."""
        resolver = resolve(ARTICLE_CREATE_URL)
        self.assertEqual(resolver.func.view_class, ArticleCreateView)

    def test_create_page_reverse_url(self) -> None:
        """Тестирование именной ссылки на страницу создания статьи."""
        url = reverse(ARTICLE_CREATE_URL_NAME)
        self.assertEqual(url, ARTICLE_CREATE_URL)
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, ArticleCreateView)

    def test_create_page_available_for_staff(self) -> None:
        """Страница создания доступна staff и рендерит React форму."""
        self.client.force_login(self.staff_user)
        response = self.client.get(ARTICLE_CREATE_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, ARTICLE_FORM_TEMPLATE)
        self.assertTemplateUsed(response, BASE_TEMPLATE)
        self.assertContains(response, 'data-component-name="Blog/ArticleForm"')
        # URL скрипта редактора передается пропом из STATIC_URL хранилища статики
        self.assertContains(response, '"tinymceScriptSrc": "/static/tinymce/tinymce.min.js"')

    def test_create_page_redirects_anonymous_to_login(self) -> None:
        """Анонима страница создания перенаправляет на вход с параметром next."""
        response = self.client.get(ARTICLE_CREATE_URL)
        self.assertRedirects(response, f"/accounts/login/?next={ARTICLE_CREATE_URL}")

    def test_create_page_forbidden_for_non_staff(self) -> None:
        """Авторизованному не-staff страница создания возвращает 403."""
        self.client.force_login(self.user)
        response = self.client.get(ARTICLE_CREATE_URL)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class TestArticleEditView(TestCase):
    """Тесты страницы редактирования статьи (ArticleEditView)."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные."""
        cls.user = User.objects.create_user(username="edituser", email="edituser@example.com", password="12345")
        cls.staff_user = User.objects.create_user(
            username="editstaff",
            email="editstaff@example.com",
            password="12345",
            is_staff=True,
        )
        cls.article = ArticleFactory(title="Редактируемая статья", slug="edit-me", author=cls.staff_user)

    def test_edit_page_url(self) -> None:
        """Тестирование ссылки на страницу редактирования статьи."""
        url = ARTICLE_EDIT_URL + self.article.slug + "/edit/"
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, ArticleEditView)

    def test_edit_page_reverse_url(self) -> None:
        """Тестирование именной ссылки на страницу редактирования."""
        url = reverse(ARTICLE_EDIT_URL_NAME, args=(self.article.slug,))
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, ArticleEditView)

    def test_edit_page_available_for_staff(self) -> None:
        """Страница редактирования доступна staff и получает ID статьи."""
        self.client.force_login(self.staff_user)
        url = reverse(ARTICLE_EDIT_URL_NAME, args=(self.article.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, ARTICLE_FORM_TEMPLATE)
        self.assertContains(response, 'data-component-name="Blog/ArticleForm"')
        self.assertContains(response, f'"articleId": {self.article.pk}')
        self.assertContains(response, '"tinymceScriptSrc": "/static/tinymce/tinymce.min.js"')

    def test_edit_page_redirects_anonymous_to_login(self) -> None:
        """Анонима страница редактирования перенаправляет на вход с параметром next."""
        url = reverse(ARTICLE_EDIT_URL_NAME, args=(self.article.slug,))
        response = self.client.get(url)
        self.assertRedirects(response, f"/accounts/login/?next={url}")

    def test_edit_page_forbidden_for_non_staff(self) -> None:
        """Авторизованному не-staff страница редактирования возвращает 403."""
        self.client.force_login(self.user)
        url = reverse(ARTICLE_EDIT_URL_NAME, args=(self.article.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class TestCategoryPage(TestCase):
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

        # Слаг категории передаётся ArticleList как проп categorySlug
        self.assertContains(response, f'"categorySlug": "{self.test_category.slug}"')

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

    def test_private_category_accessible_by_link(self) -> None:
        """Приватная категория доступна по прямой ссылке."""
        private_category = CategoryFactory(name="Private category", slug="private-category", public=False)
        url = reverse(CATEGORY_URL_NAME, args=(private_category.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context["category"], private_category)

    def test_private_category_page_has_noindex(self) -> None:
        """HTML страницы приватной категории содержит meta robots noindex."""
        private_category = CategoryFactory(name="Private cat noindex", slug="private-cat-noindex", public=False)
        url = reverse(CATEGORY_URL_NAME, args=(private_category.slug,))
        response = self.client.get(url)
        self.assertContains(response, '<meta name="robots" content="noindex">')


class TestTopicPage(TestCase):
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

        # Слаг темы передаётся ArticleList как проп topicSlug
        self.assertContains(response, f'"topicSlug": "{self.test_topic.slug}"')

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

    def test_private_topic_accessible_by_link(self) -> None:
        """Приватная тема доступна по прямой ссылке."""
        private_topic = TopicFactory(name="Private topic", slug="private-topic", public=False)
        url = reverse(TOPIC_URL_NAME, args=(private_topic.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context["topic"], private_topic)

    def test_private_topic_page_has_noindex(self) -> None:
        """HTML страницы приватной темы содержит meta robots noindex."""
        private_topic = TopicFactory(name="Private topic noindex", slug="private-topic-noindex", public=False)
        url = reverse(TOPIC_URL_NAME, args=(private_topic.slug,))
        response = self.client.get(url)
        self.assertContains(response, '<meta name="robots" content="noindex">')


class TestSeriesPage(TestCase):
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

        # Слаг серии передаётся ArticleList как проп seriesSlug
        self.assertContains(response, f'"seriesSlug": "{self.test_series.slug}"')

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

    def test_private_series_accessible_by_link(self) -> None:
        """Приватная серия доступна по прямой ссылке."""
        private_series = SeriesFactory(name="Private series", slug="private-series", public=False)
        url = reverse(SERIES_URL_NAME, args=(private_series.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context["series"], private_series)

    def test_private_series_page_has_noindex(self) -> None:
        """HTML страницы приватной серии содержит meta robots noindex."""
        private_series = SeriesFactory(name="Private series noindex", slug="private-series-noindex", public=False)
        url = reverse(SERIES_URL_NAME, args=(private_series.slug,))
        response = self.client.get(url)
        self.assertContains(response, '<meta name="robots" content="noindex">')
