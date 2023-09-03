import os

from django.test import SimpleTestCase
from dotenv import load_dotenv

from personal_website.utils import str_to_bool

test_s3 = str_to_bool(os.getenv("TEST_S3"))


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
