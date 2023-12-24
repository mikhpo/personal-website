import os
from pathlib import Path

from django.core.files.storage import FileSystemStorage
from django.test import SimpleTestCase
from dotenv import load_dotenv

from project.storages import select_storage


class FileSystemStorageTests(SimpleTestCase):
    """
    Проверка доступа к хранилищу на основе локальной файловой системы.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_dotenv()

    def test_storage_dir_location(self):
        """
        Проверить, что директория хранилища существует.
        """
        storage_dir = os.getenv("STORAGE_ROOT")
        self.assertTrue(os.path.exists(storage_dir))

    def test_select_storage(self):
        """
        Селектор хранилища возвращает тестовое хранилище.
        """
        storage = select_storage()
        self.assertIsInstance(storage, FileSystemStorage)
        storage_name = Path(storage.location).name
        self.assertEqual(storage_name, "temp")
