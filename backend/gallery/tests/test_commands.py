"""Тесты для команд управления галереи."""

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from gallery.models import Album, Photo, Tag


class TestGenerateGalleryObjectsCommand(TestCase):
    """Тесты для команды generate_gallery_objects."""

    def setUp(self) -> None:
        """Подготовка тестовых данных."""
        self.out = StringIO()

    def test_command_output_with_default_parameters(self) -> None:
        """Тест команды с параметрами по умолчанию."""
        with patch("sys.stdout", self.out):
            call_command("generate_gallery_objects", stdout=self.out)

        output = self.out.getvalue()
        self.assertIn("Создание тегов галереи...", output)
        self.assertIn("Создание альбомов галереи...", output)
        self.assertIn("Создание 50 фотографий...", output)
        self.assertIn("Создано 50 фотографий", output)
        self.assertIn("Успешно сгенерированы тестовые объекты для галереи: 50 фотографий", output)

    def test_command_with_custom_parameters_creates_objects_and_outputs_correctly(self) -> None:
        """Тест команды с пользовательскими параметрами, проверяющий и вывод, и создание объектов."""
        # Убедимся, что база данных пуста перед началом
        self.assertEqual(Photo.objects.count(), 0)
        self.assertEqual(Album.objects.count(), 0)
        self.assertEqual(Tag.objects.count(), 0)

        # Вызываем команду с пользовательскими параметрами
        with patch("sys.stdout", self.out):
            call_command(
                "generate_gallery_objects",
                "--photos",
                "5",
                "--albums",
                "2",
                "--tags",
                "3",
                stdout=self.out,
            )

        # Проверяем вывод команды
        output = self.out.getvalue()
        self.assertIn("Создание 5 фотографий...", output)
        self.assertIn("Создано 5 фотографий", output)
        self.assertIn("Успешно сгенерированы тестовые объекты для галереи: 5 фотографий", output)

        # Проверяем, что объекты были созданы в базе данных
        self.assertEqual(Photo.objects.count(), 5)
        self.assertGreaterEqual(Album.objects.count(), 2)
        self.assertGreaterEqual(Tag.objects.count(), 3)
