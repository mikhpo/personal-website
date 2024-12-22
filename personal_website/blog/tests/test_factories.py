"""Тесты фабрик для генерации экземпляров моделей со случайными данными."""

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.test import TestCase

from blog.factories import ArticleFactory, CategoryFactory, CommentFactory, SeriesFactory, TopicFactory
from blog.models import Article, Category, Comment, Series, Topic
from gallery.utils import is_image

if TYPE_CHECKING:
    from django.db.models import QuerySet


class TestCategoryFactory(TestCase):
    """Тесты фабрики для создания категорий статей в блоге."""

    def test_category_factory_instance(self) -> None:
        """Фабрика возвращает объект категории."""
        category = CategoryFactory()
        self.assertIsInstance(category, Category)

    def test_category_factory_image_field(self) -> None:
        """Поле изображения объекта содержит настоящее изображение."""
        category = CategoryFactory()
        is_valid_image = is_image(category.image)
        self.assertTrue(is_valid_image)


class TestTopicFactory(TestCase):
    """Тесты фабрики для создания темы статьи в блоге."""

    def test_topic_factory_instance(self) -> None:
        """Фабрика возвращает объект темы."""
        topic = TopicFactory()
        self.assertIsInstance(topic, Topic)

    def test_topic_factory_image_field(self) -> None:
        """Поле изображения объекта содержит настоящее изображение."""
        topic = TopicFactory()
        is_valid_image = is_image(topic.image)
        self.assertTrue(is_valid_image)


class TestSeriesFactory(TestCase):
    """Тесты фабрики для создания серии статей в блоге."""

    def test_series_factory_instance(self) -> None:
        """Фабрика возвращает объект серии."""
        series = SeriesFactory()
        self.assertIsInstance(series, Series)

    def test_series_factory_image_field(self) -> None:
        """Поле изображения объекта содержит настоящее изображение."""
        series = SeriesFactory()
        is_valid_image = is_image(series.image)
        self.assertTrue(is_valid_image)


class TestArticleFactory(TestCase):
    """Тесты фабрики для генерации статей."""

    def test_article_factory_instance(self) -> None:
        """Фабрика возвращает объект статьи."""
        article = ArticleFactory()
        self.assertIsInstance(article, Article)

    def test_article_factory_image_field(self) -> None:
        """Поле изображения содержит настоящее изображение."""
        article = ArticleFactory()
        is_valid_image = is_image(article.image)
        self.assertTrue(is_valid_image)

    def test_article_factory_create_series(self) -> None:
        """Связанные серии создаются."""
        series = tuple(SeriesFactory() for _ in range(3))
        article = ArticleFactory.create(series=series)
        series_qs: QuerySet[Topic] = article.series.all()
        self.assertTrue(series_qs.exists())

    def test_article_factory_create_topics(self) -> None:
        """Связанные темы создаются."""
        topics = tuple(TopicFactory() for _ in range(3))
        article = ArticleFactory.create(topics=topics)
        topic_qs: QuerySet[Topic] = article.topics.all()
        self.assertTrue(topic_qs.exists())

    def test_article_factory_create_categories(self) -> None:
        """Связанные темы создаются."""
        categories = tuple(CategoryFactory() for _ in range(3))
        article = ArticleFactory.create(categories=categories)
        category_qs: QuerySet[Topic] = article.categories.all()
        self.assertTrue(category_qs.exists())


class TestCommentFactory(TestCase):
    """Тесты фабрики для создания комментариев к статьям."""

    def test_comment_factory_instance(self) -> None:
        """Фабрика возвращает объект комментария."""
        comment = CommentFactory()
        self.assertIsInstance(comment, Comment)

    def test_comment_factory_subfactories(self) -> None:
        """Фабрика комментария создает статью и автора через подфабрики."""
        comment = CommentFactory()
        self.assertIsInstance(comment.article, Article)
        self.assertIsInstance(comment.author, User)
