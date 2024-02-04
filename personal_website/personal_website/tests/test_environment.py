"""Тесты переменных окружения."""
import os
from pathlib import Path
from unittest import skipIf

from django.conf import settings
from django.test import SimpleTestCase
from dotenv import load_dotenv

from personal_website.utils import is_running_in_container


@skipIf(is_running_in_container(), "Не актуально для запуска из контейнера")
class SecretsTests(SimpleTestCase):
    """Проверка на то, что секреты загружаются."""

    environment_variables = (
        "DEBUG",
        "SECRET_KEY",
        "STORAGE_ROOT",
        "BACKUP_ROOT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "EMAIL_HOST_USER",
        "EMAIL_HOST_PASSWORD",
    )

    def test_dotenv_path(self) -> None:
        """Проверка на наличие в коревной директории проекта файла .env с переменными окружения."""
        dotenv_filepath = Path(settings.PROJECT_DIR) / ".env"
        dotenv_exists = Path(dotenv_filepath).exists()
        self.assertTrue(dotenv_exists)

    def test_dotenv_load(self) -> None:
        """Проверка на корректность загрузки переменных окружения из .env файла."""
        self.assertTrue(load_dotenv())
        for variable in self.environment_variables:
            self.assertIsNotNone(os.environ[variable])
