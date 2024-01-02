import os
from unittest import skipIf

from django.conf import settings
from django.test import SimpleTestCase
from dotenv import load_dotenv

from personal_website.utils import is_running_in_container

ENVIRONMENT_VARIABLES = (
    "DEBUG",
    "SECRET_KEY",
    "STORAGE_ROOT",
    "BACKUP_ROOT",
    "POSTGRES_NAME",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
)


@skipIf(is_running_in_container(), "Не актуально для запуска из контейнера")
class SecretsTests(SimpleTestCase):
    """
    Проверка на то, что секреты загружаются.
    """

    def test_dotenv_path(self):
        """
        Проверка на наличие в коревной директории проекта файла .env с переменными окружения.
        """
        dotenv_filepath = os.path.join(settings.PROJECT_DIR, ".env")
        self.assertTrue(os.path.exists(dotenv_filepath))

    def test_dotenv_load(self):
        """
        Проверка на корректность загрузки переменных окружения из .env файла.
        """
        self.assertTrue(load_dotenv())
        for variable in ENVIRONMENT_VARIABLES:
            self.assertIsNotNone(os.environ[variable])
