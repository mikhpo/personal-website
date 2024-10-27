"""Тесты фабрик для генерации экземпляров моделей со случайными данными."""
from django.test import TestCase

from blog.factories import CategoryFactory, SeriesFactory, TopicFactory
from blog.models import Category, Series, Topic
from gallery.utils import is_image


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
        topic: Topic = TopicFactory()
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
        series: Series = SeriesFactory()
        is_valid_image = is_image(series.image)
        self.assertTrue(is_valid_image)
