"""Тесты API представлений блога."""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from rest_framework.test import APITestCase

from blog.factories import ArticleFactory, CategoryFactory, CommentFactory, SeriesFactory, TopicFactory

User = get_user_model()


class TestCategoryViewSet(APITestCase):
    """Тесты для CategoryViewSet."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.category1 = CategoryFactory(name="Разработка", description="Статьи о разработке", public=True)
        cls.category2 = CategoryFactory(name="Путешествия", description="Статьи о путешествиях", public=True)
        cls.category3 = CategoryFactory(name="Личное", description="Личные записи", public=False)
        super().setUpTestData()

    def test_list_categories(self) -> None:
        """Получение списка категорий."""
        url = "/api/blog/categories/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # Только публичные категории
        self.assertEqual(len(response.data["results"]), 2)

    def test_retrieve_category(self) -> None:
        """Детальный просмотр категории."""
        url = f"/api/blog/categories/{self.category1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.category1.name)
        self.assertEqual(response.data["slug"], self.category1.slug)
        self.assertEqual(response.data["description"], self.category1.description)

    def test_search_categories(self) -> None:
        """Поиск категорий по названию и описанию."""
        url = "/api/blog/categories/"
        response = self.client.get(url, {"search": "Разработка"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Разработка")

    def test_ordering_categories(self) -> None:
        """Сортировка категорий по имени."""
        url = "/api/blog/categories/"
        response = self.client.get(url, {"ordering": "name"})
        self.assertEqual(response.status_code, 200)
        results = response.data["results"]
        names = [cat["name"] for cat in results]
        self.assertEqual(names, sorted(names))

    def test_list_categories_unauthenticated(self) -> None:
        """Неаутентифицированные видят только публичные категории."""
        url = "/api/blog/categories/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # Только публичные

    def test_list_categories_staff_same_as_anonymous(self) -> None:
        """Список категорий для staff совпадает с анонимным (только public)."""
        staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)
        self.client.force_authenticate(user=staff_user)
        url = "/api/blog/categories/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # Только публичные

    def test_retrieve_private_category_accessible_by_link(self) -> None:
        """Приватная категория доступна по прямой ссылке."""
        url = f"/api/blog/categories/{self.category3.pk}/"
        # Аноним
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.category3.name)
        # Staff видит тот же результат
        staff_user = User.objects.create_user(username="staffuser2", password="testpass123", is_staff=True)
        self.client.force_authenticate(user=staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.category3.name)


class TestTopicViewSet(APITestCase):
    """Тесты для TopicViewSet."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.topic1 = TopicFactory(name="Горы", description="Горные походы", public=True)
        cls.topic2 = TopicFactory(name="Дети", description="О детях", public=True)
        cls.topic3 = TopicFactory(name="Личное", description="Личные темы", public=False)
        super().setUpTestData()

    def test_list_topics(self) -> None:
        """Получение списка тем."""
        url = "/api/blog/topics/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # Только публичные темы

    def test_retrieve_topic(self) -> None:
        """Детальный просмотр темы."""
        url = f"/api/blog/topics/{self.topic1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.topic1.name)

    def test_search_topics(self) -> None:
        """Поиск тем по названию и описанию."""
        url = "/api/blog/topics/"
        response = self.client.get(url, {"search": "Горы"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Горы")

    def test_list_topics_unauthenticated(self) -> None:
        """Неаутентифицированные видят только публичные темы."""
        url = "/api/blog/topics/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_list_topics_staff_same_as_anonymous(self) -> None:
        """Список тем для staff совпадает с анонимным (только public)."""
        staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)
        self.client.force_authenticate(user=staff_user)
        url = "/api/blog/topics/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_retrieve_private_topic_accessible_by_link(self) -> None:
        """Приватная тема доступна по прямой ссылке."""
        url = f"/api/blog/topics/{self.topic3.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.topic3.name)


class TestSeriesViewSet(APITestCase):
    """Тесты для SeriesViewSet."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.series1 = SeriesFactory(name="Лангтанг-трек", description="Трек по Лангтангу", public=True)
        cls.series2 = SeriesFactory(name="Тоскана", description="Осенняя Тоскана", public=True)
        cls.series3 = SeriesFactory(name="Личное", description="Личные серии", public=False)
        super().setUpTestData()

    def test_list_series(self) -> None:
        """Получение списка серий."""
        url = "/api/blog/series/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # Только публичные серии

    def test_retrieve_series(self) -> None:
        """Детальный просмотр серии."""
        url = f"/api/blog/series/{self.series1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.series1.name)

    def test_search_series(self) -> None:
        """Поиск серий по названию и описанию."""
        url = "/api/blog/series/"
        response = self.client.get(url, {"search": "Лангтанг"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Лангтанг-трек")

    def test_list_series_unauthenticated(self) -> None:
        """Неаутентифицированные видят только публичные серии."""
        url = "/api/blog/series/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_list_series_staff_same_as_anonymous(self) -> None:
        """Список серий для staff совпадает с анонимным (только public)."""
        staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)
        self.client.force_authenticate(user=staff_user)
        url = "/api/blog/series/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_retrieve_private_series_accessible_by_link(self) -> None:
        """Приватная серия доступна по прямой ссылке."""
        url = f"/api/blog/series/{self.series3.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.series3.name)


class TestArticleViewSet(APITestCase):
    """Тесты для ArticleViewSet."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)

        # Создать категории, темы, серии
        cls.category1 = CategoryFactory(name="Python", public=True)
        cls.category2 = CategoryFactory(name="Django", public=True)
        cls.topic1 = TopicFactory(name="Backend", public=True)
        cls.series1 = SeriesFactory(name="Django для начинающих", public=True)

        # Создать статьи
        cls.article1 = ArticleFactory(
            title="Введение в Django",
            description="Статья о Django",
            content="Django - это веб-фреймворк",
            public=True,
            author=cls.user,
        )
        cls.article1.categories.add(cls.category1, cls.category2)
        cls.article1.topics.add(cls.topic1)
        cls.article1.series.add(cls.series1)

        cls.article2 = ArticleFactory(
            title="Продвинутый Python",
            description="Статья о Python",
            content="Python - это язык программирования",
            public=True,
            author=cls.user,
        )
        cls.article2.categories.add(cls.category1)

        cls.article3 = ArticleFactory(
            title="Личная статья",
            description="Личная запись",
            content="Личный контент",
            public=False,
            author=cls.user,
        )

        # Создать комментарии
        cls.comment1 = CommentFactory(article=cls.article1, author=cls.user)
        cls.comment2 = CommentFactory(article=cls.article1, author=cls.staff_user)
        super().setUpTestData()

    def test_list_articles(self) -> None:
        """Получение списка статей."""
        url = "/api/blog/articles/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # Только публичные статьи

    def test_retrieve_article(self) -> None:
        """Детальный просмотр статьи с комментариями."""
        url = f"/api/blog/articles/{self.article1.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.article1.title)
        self.assertEqual(len(response.data["comments"]), 2)
        self.assertIn("author_username", response.data)

    def test_filter_articles_by_category(self) -> None:
        """Фильтрация статей по категории."""
        url = "/api/blog/articles/"
        response = self.client.get(url, {"categories__slug": self.category1.slug})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # Обе статьи в категории Python

    def test_filter_articles_by_topic(self) -> None:
        """Фильтрация статей по теме."""
        url = "/api/blog/articles/"
        response = self.client.get(url, {"topics__slug": self.topic1.slug})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_filter_articles_by_series(self) -> None:
        """Фильтрация статей по серии."""
        url = "/api/blog/articles/"
        response = self.client.get(url, {"series__slug": self.series1.slug})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_search_articles(self) -> None:
        """Поиск статей по заголовку, описанию и содержанию."""
        url = "/api/blog/articles/"
        response = self.client.get(url, {"search": "Django"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Введение в Django")

    def test_ordering_articles(self) -> None:
        """Сортировка статей по дате публикации."""
        url = "/api/blog/articles/"
        response = self.client.get(url, {"ordering": "-published_at"})
        self.assertEqual(response.status_code, 200)

    def test_list_articles_unauthenticated(self) -> None:
        """Неаутентифицированные видят только публичные статьи."""
        url = "/api/blog/articles/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_list_articles_staff_same_as_anonymous(self) -> None:
        """Список статей для staff совпадает с анонимным (только public)."""
        self.client.force_authenticate(user=self.staff_user)
        url = "/api/blog/articles/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # Только публичные статьи

    def test_retrieve_private_article_accessible_by_link(self) -> None:
        """Приватная статья доступна по прямой ссылке.

        В list показываем только public=True, но retrieve любого объекта
        по прямой ссылке доступен всем пользователям.
        """
        url = f"/api/blog/articles/{self.article3.pk}/"
        # Аноним
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.article3.title)
        # Staff видит тот же результат
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.article3.title)


@pytest.mark.skipif(connection.vendor != "postgresql", reason="Полнотекстовый поиск работает только на PostgreSQL")
class TestArticleFullTextSearch(APITestCase):
    """Полнотекстовый поиск статей: морфология и релевантность на PostgreSQL."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.user = User.objects.create_user(username="ftsuser", password="testpass123")
        super().setUpTestData()

    def test_morphology_finds_word_forms(self) -> None:
        """Запрос "статья" находит статью со словоформой "статьи"."""
        article = ArticleFactory(
            title="Путевые заметки",
            description="Статьи о путешествиях",
            content="Контент без ключевого слова",
            public=True,
            author=self.user,
        )
        url = "/api/blog/articles/"
        response = self.client.get(url, {"search": "статья"})
        self.assertEqual(response.status_code, 200)
        slugs = [item["slug"] for item in response.data["results"]]
        self.assertIn(article.slug, slugs)

    def test_relevance_title_above_content(self) -> None:
        """Статья с совпадением в заголовке ранжируется выше совпадения только в контенте."""
        title_match = ArticleFactory(
            title="Велосипед",
            description="Описание прогулки",
            content="Текст о прогулке",
            public=True,
            author=self.user,
        )
        content_match = ArticleFactory(
            title="Прогулка по парку",
            description="Заметки о парке",
            content="Вдалеке проехал велосипед",
            public=True,
            author=self.user,
        )
        url = "/api/blog/articles/"
        response = self.client.get(url, {"search": "велосипед"})
        self.assertEqual(response.status_code, 200)
        slugs = [item["slug"] for item in response.data["results"]]
        self.assertEqual(slugs, [title_match.slug, content_match.slug])


class TestCommentViewSet(APITestCase):
    """Тесты для CommentViewSet."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.user2 = User.objects.create_user(username="testuser2", password="testpass123")
        cls.staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)

        # Создать статью
        cls.article = ArticleFactory(title="Тестовая статья", public=True, author=cls.user)

        # Создать комментарии
        cls.comment1 = CommentFactory(article=cls.article, author=cls.user, content="Первый комментарий")
        cls.comment2 = CommentFactory(article=cls.article, author=cls.user2, content="Второй комментарий")
        super().setUpTestData()

    def test_list_comments(self) -> None:
        """Получение списка комментариев."""
        url = "/api/blog/comments/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_retrieve_comment(self) -> None:
        """Детальный просмотр комментария."""
        url = f"/api/blog/comments/{self.comment1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content"], self.comment1.content)
        self.assertEqual(response.data["author_username"], self.user.username)

    def test_filter_comments_by_article(self) -> None:
        """Фильтрация комментариев по статье."""
        url = "/api/blog/comments/"
        response = self.client.get(url, {"article__slug": self.article.slug})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_create_comment_authenticated(self) -> None:
        """Успешное создание комментария авторизованным пользователем."""
        url = "/api/blog/comments/"
        data = {
            "article": self.article.pk,
            "content": "Новый комментарий",
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["content"], "Новый комментарий")
        self.assertEqual(response.data["author_username"], self.user.username)

    def test_create_comment_unauthenticated(self) -> None:
        """Возвращает 401 для неавторизованных."""
        url = "/api/blog/comments/"
        data = {
            "article": self.article.id,
            "content": "Новый комментарий",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)

    def test_create_comment_sets_author_automatically(self) -> None:
        """Author автоматически устанавливается из request.user."""
        url = "/api/blog/comments/"
        data = {
            "article": self.article.pk,
            "content": "Тест авторства",
        }
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["author_username"], self.user2.username)

    def test_update_comment_by_author(self) -> None:
        """Автор может обновить свой комментарий."""
        url = f"/api/blog/comments/{self.comment1.pk}/"
        data = {
            "article": self.article.pk,
            "content": "Обновленный комментарий",
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content"], "Обновленный комментарий")

    def test_update_comment_by_non_author(self) -> None:
        """Не автор не может обновить (403)."""
        url = f"/api/blog/comments/{self.comment1.pk}/"
        data = {"content": "Чужой комментарий"}
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 403)

    def test_partial_update_comment(self) -> None:
        """PATCH запрос работает."""
        url = f"/api/blog/comments/{self.comment1.id}/"
        data = {"content": "Частично обновленный"}
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content"], "Частично обновленный")

    def test_delete_comment_by_author(self) -> None:
        """Автор может удалить свой комментарий."""
        url = f"/api/blog/comments/{self.comment1.id}/"
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_delete_comment_by_non_author(self) -> None:
        """Не автор не может удалить (403)."""
        url = f"/api/blog/comments/{self.comment1.pk}/"
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
