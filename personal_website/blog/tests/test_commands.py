"""Тесты для команд управления блога."""

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from blog.models import Article, Category, Series, Topic


class TestGenerateBlogObjectsCommand(TestCase):
    """Тесты для команды generate_blog_objects."""

    def setUp(self) -> None:
        """Подготовка тестовых данных."""
        self.out = StringIO()

    def test_command_output_with_default_parameters(self) -> None:
        """Тест команды с параметрами по умолчанию."""
        with patch("sys.stdout", self.out):
            call_command("generate_blog_objects", stdout=self.out)

        output = self.out.getvalue()
        self.assertIn("Создание пользователей...", output)
        self.assertIn("Создание категорий блога...", output)
        self.assertIn("Создание серий блога...", output)
        self.assertIn("Создание тем блога...", output)
        self.assertIn("Создание 20 статей...", output)
        self.assertIn("Создано 20 статей", output)
        self.assertIn("Успешно сгенерированы тестовые объекты для блога: 20 статей", output)

    def test_command_with_custom_parameters_creates_objects_and_outputs_correctly(self) -> None:
        """Тест команды с пользовательскими параметрами, проверяющий и вывод, и создание объектов."""
        # Убедимся, что база данных пуста перед началом
        self.assertEqual(Article.objects.count(), 0)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Series.objects.count(), 0)
        self.assertEqual(Topic.objects.count(), 0)

        # Вызываем команду с пользовательскими параметрами
        with patch("sys.stdout", self.out):
            call_command(
                "generate_blog_objects",
                "--articles",
                "5",
                "--categories",
                "3",
                "--series",
                "2",
                "--topics",
                "4",
                stdout=self.out,
            )

        # Проверяем вывод команды
        output = self.out.getvalue()
        self.assertIn("Создание 5 статей...", output)
        self.assertIn("Создано 5 статей", output)
        self.assertIn("Успешно сгенерированы тестовые объекты для блога: 5 статей", output)

        # Проверяем, что объекты были созданы в базе данных
        self.assertEqual(Article.objects.count(), 5)
        self.assertGreaterEqual(Category.objects.count(), 3)
        self.assertGreaterEqual(Series.objects.count(), 2)
        self.assertGreaterEqual(Topic.objects.count(), 4)
