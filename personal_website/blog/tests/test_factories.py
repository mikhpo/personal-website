"""Тесты фабрик для генерации экземпляров моделей со случайными данными."""
from django.test import TestCase

from blog.factories import CategoryFactory, TopicFactory
from blog.models import Category, Topic
from gallery.utils import is_image


class TestCategoryFactory(TestCase):
    """Тесты фабрики для создания категорий."""

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
    """Тесты фабрики для создания темы."""

    def test_topic_factory_instance(self) -> None:
        """Фабрика возвращает объект темы."""
        topic = TopicFactory()
        self.assertIsInstance(topic, Topic)

    def test_topic_factory_image_field(self) -> None:
        """Поле изображения объекта содержит настоящее изображение."""
        topic: Topic = TopicFactory()
        is_valid_image = is_image(topic.image)
        self.assertTrue(is_valid_image)
