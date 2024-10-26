"""Тесты фабрик для генерации экземпляров моделей со случайными данными."""
from django.test import TestCase

from blog.factories import CategoryFactory
from blog.models import Category
from gallery.utils import is_image


class TestCategoryFactory(TestCase):
    """Тесты фабрики для создания категорий."""

    def test_category_factory_instance(self) -> None:
        """Фабрика возвращает объект категории."""
        category = CategoryFactory()
        self.assertIsInstance(category, Category)

    def test_category_factory_image_field(self) -> None:
        """Поле изображения объекта содержит настоящее изображение."""
        category: Category = CategoryFactory()
        is_valid_image = is_image(category.image)
        self.assertTrue(is_valid_image)
