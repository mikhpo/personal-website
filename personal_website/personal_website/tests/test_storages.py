"""Тесты файловых хранилищ."""

from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.test import SimpleTestCase

from personal_website.storages import select_storage


class FileSystemStorageTests(SimpleTestCase):
    """Проверка доступа к хранилищу на основе локальной файловой системы."""

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D102
        super().setUpClass()

    def test_storage_dir_location(self) -> None:
        """Проверить, что директория хранилища существует."""
        storage_dir = settings.MEDIA_ROOT
        path_exists = Path(storage_dir).exists()
        self.assertTrue(path_exists)

    def test_select_storage(self) -> None:
        """Селектор хранилища возвращает тестовое хранилище."""
        storage = select_storage()
        self.assertIsInstance(storage, FileSystemStorage)
        storage_name = Path(storage.location).name
        self.assertEqual(storage_name, "temp")
