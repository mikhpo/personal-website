"""Тесты представлений блога в административном интерфейсе Django."""

from http import HTTPStatus

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from faker import Faker
from faker_file.providers.jpeg_file import JpegFileProvider  # type: ignore[import-untyped]

from blog.apps import BlogConfig
from blog.factories import ArticleFactory, CategoryFactory, CommentFactory, SeriesFactory, TopicFactory
from blog.models import Article, Category, Comment, Series, Topic
from personal_website.utils import format_local_datetime, generate_random_text

FAKER = Faker()


class BlogAdminTest(TestCase):
    """Тестирование функциональности раздела блога в административном интерфейсе Django."""

    ADMIN_URL = "/admin/"

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.superuser: User = User.objects.create_superuser(username="testadmin", password="12345")
        cls.series: Series = SeriesFactory(image=None)
        cls.topic: Topic = TopicFactory(image=None)
        cls.category: Category = CategoryFactory(image=None)
        cls.article: Article = ArticleFactory(author=cls.superuser)
        cls.comment: Comment = CommentFactory(article=cls.article, author=cls.superuser)
        cls.jpeg_raw = JpegFileProvider(FAKER).jpeg_file(raw=True)

    def setUp(self) -> None:
        """Авторизоваться как пользователь с правами персонала."""
        self.client.login(username="testadmin", password="12345")

    def test_blog_admin_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображется раздел блога."""
        app_verbose_name = BlogConfig.verbose_name
        response = self.client.get(self.ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, app_verbose_name)
        response = self.client.get(self.ADMIN_URL + "blog/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for action in ["Добавить", "Изменить"]:
            self.assertContains(response, action)

    def test_article_admin_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображается модель статьи."""
        articles_verbose_name = Article._meta.verbose_name_plural  # noqa: SLF001
        self.assertNotEqual(articles_verbose_name, None)
        response = self.client.get(self.ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, str(articles_verbose_name))
        response = self.client.get(self.ADMIN_URL + "blog/article/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_comment_admin_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображается модель комментария."""
        comments_verbose_name = Comment._meta.verbose_name_plural  # noqa: SLF001
        self.assertNotEqual(comments_verbose_name, None)
        response = self.client.get(self.ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, str(comments_verbose_name))
        response = self.client.get(self.ADMIN_URL + "blog/comment/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_series_admin_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображается модель серии."""
        series_verbose_name = Series._meta.verbose_name_plural  # noqa: SLF001
        self.assertNotEqual(series_verbose_name, None)
        response = self.client.get(self.ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, str(series_verbose_name))
        response = self.client.get(self.ADMIN_URL + "blog/series/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_topic_admin_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображается модель темы."""
        topics_verbose_name = Topic._meta.verbose_name_plural  # noqa: SLF001
        self.assertNotEqual(topics_verbose_name, None)
        response = self.client.get(self.ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, str(topics_verbose_name))
        response = self.client.get(self.ADMIN_URL + "blog/topic/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_category_admin_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображается модель категории."""
        categories_verbose_name = Category._meta.verbose_name_plural  # noqa: SLF001
        self.assertNotEqual(categories_verbose_name, None)
        response = self.client.get(self.ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, str(categories_verbose_name))
        response = self.client.get(self.ADMIN_URL + "blog/category/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_articles_admin_list_displayed(self) -> None:
        """Проверяет, что список статей в административной панели отображает нужные поля."""
        response = self.client.get(self.ADMIN_URL + "blog/article/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for value in [
            self.article.title,
            format_local_datetime(self.article.published_at),
            format_local_datetime(self.article.modified_at),
            self.article.public,
            self.article.author,
        ]:
            self.assertContains(response, value)

    def test_comments_admin_list_displayed(self) -> None:
        """Проверяет, что список комментариев в административной панели отображает нужные поля."""
        response = self.client.get(self.ADMIN_URL + "blog/comment/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for value in [
            self.comment.article,
            self.comment.author,
            format_local_datetime(self.comment.posted),
        ]:
            self.assertContains(response, value)

    def test_series_admin_list_displayed(self) -> None:
        """Проверяет, что список серий в административной панели отображает нужные поля."""
        response = self.client.get(self.ADMIN_URL + "blog/series/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for value in [
            self.series.name,
            self.series.slug,
            self.series.image,
            self.series.public,
        ]:
            self.assertContains(response, value)

    def test_topic_admin_list_displayed(self) -> None:
        """Проверяет, что список тем в административной панели отображает нужные поля."""
        response = self.client.get(self.ADMIN_URL + "blog/topic/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for value in [
            self.topic.name,
            self.topic.slug,
            self.topic.image,
            self.topic.public,
        ]:
            self.assertContains(response, value)

    def test_category_admin_list_displayed(self) -> None:
        """Проверяет, что список категорий в административной панели отображает нужные поля."""
        response = self.client.get(self.ADMIN_URL + "blog/category/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for value in [
            self.category.name,
            self.category.slug,
            self.category.image,
            self.category.public,
        ]:
            self.assertContains(response, value)

    def test_article_created_via_admin(self) -> None:
        """Проверяет успешность добавления статьи через административную панель."""
        response = self.client.post(self.ADMIN_URL + "blog/article/add/", data={"title": "Test article 2"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.client.post(
            self.ADMIN_URL + "blog/article/add/",
            data={"content": generate_random_text(50)},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.client.post(
            self.ADMIN_URL + "blog/article/add/",
            data={"title": "Test article 2", "content": generate_random_text(50)},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Article.objects.filter(title="Test article 2").exists())
        self.assertNotEqual(Article.objects.get(title="Test article 2").published_at, None)

    def test_comment_created_via_admin(self) -> None:
        """Проверяет успешность добавления комментария через административную панель."""
        response = self.client.post(
            self.ADMIN_URL + "blog/comment/add/",
            data={
                "content": "Test comment",
                "article": self.article.pk,
                "author": self.superuser.pk,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            Comment.objects.filter(content="Test comment", article=self.article, author=self.superuser).exists(),
        )

    def test_series_created_via_admin(self) -> None:
        """Проверяет успешность добавления серии через административную панель."""
        response = self.client.post(self.ADMIN_URL + "blog/series/add/", data={"name": "Test series 2"})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Series.objects.filter(name="Test series 2").exists())

    def test_series_fields_changed(self) -> None:
        """Проверка на корректность обновления полей и обложки серии."""
        # Проверить начальный статус - отсутствие изображения.
        self.assertFalse(bool(self.series.image))

        # Отправить форму с новыми данными и изображением через административный интерфейс.
        series_change_url = self.ADMIN_URL + f"blog/series/{self.series.pk}/change/"
        new_series_data: Series = SeriesFactory.build()
        response = self.client.post(
            series_change_url,
            data={
                "name": new_series_data.name,
                "description": new_series_data.description,
                "public": new_series_data.public,
                "image": SimpleUploadedFile(name=FAKER.file_name(category="image"), content=self.jpeg_raw),
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Проверить обновленные значения полей.
        self.series.refresh_from_db()
        self.assertEqual(self.series.name, new_series_data.name)
        self.assertTrue(bool(self.series.image))

    def test_topic_created_via_admin(self) -> None:
        """Проверяет успешность добавления темы через административную панель."""
        response = self.client.post(self.ADMIN_URL + "blog/topic/add/", data={"name": "Test topic 2"})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Topic.objects.filter(name="Test topic 2").exists())

    def test_topic_fields_changed(self) -> None:
        """Проверка на корректность обновления полей и обложки темы."""
        # Проверить начальный статус - отсутствие изображения.
        self.assertFalse(bool(self.topic.image))

        # Отправить форму с новыми данными и изображением через административный интерфейс.
        topic_change_url = self.ADMIN_URL + f"blog/topic/{self.topic.pk}/change/"
        new_topic_data: Topic = TopicFactory.build()
        response = self.client.post(
            topic_change_url,
            data={
                "name": new_topic_data.name,
                "description": new_topic_data.description,
                "public": new_topic_data.public,
                "image": SimpleUploadedFile(name=FAKER.file_name(category="image"), content=self.jpeg_raw),
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Проверить обновленные значения полей.
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.name, new_topic_data.name)
        self.assertTrue(bool(self.topic.image))

    def test_category_created_via_admin(self) -> None:
        """Проверяет успешность добавления категории через административную панель."""
        response = self.client.post(self.ADMIN_URL + "blog/category/add/", data={"name": "Test category 2"})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Category.objects.filter(name="Test category 2").exists())

    def test_category_fields_changed(self) -> None:
        """Проверка на корректность обновления полей и обложки категории."""
        # Проверить начальный статус - отсутствие изображения.
        self.assertFalse(bool(self.category.image))

        # Отправить форму с новыми данными и изображением через административный интерфейс.
        category_change_url = self.ADMIN_URL + f"blog/category/{self.category.pk}/change/"
        new_category_data: Category = CategoryFactory.build()
        response = self.client.post(
            category_change_url,
            data={
                "name": new_category_data.name,
                "description": new_category_data.description,
                "public": new_category_data.public,
                "image": SimpleUploadedFile(name=FAKER.file_name(category="image"), content=self.jpeg_raw),
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Проверить обновленные значения полей.
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, new_category_data.name)
        self.assertTrue(bool(self.category.image))
