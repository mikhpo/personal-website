import os
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase
from faker import Faker
from faker_file.providers.jpeg_file import JpegFileProvider
from faker_file.storages.filesystem import FileSystemStorage

from personal_website.utils import calculate_path_size, list_file_paths

temp_root = os.getenv("TEMP_ROOT")
test_dir = Path(__file__).resolve().stem

FAKER = Faker()
FS_STORAGE = FileSystemStorage(
    root_path=temp_root,
    rel_path=test_dir,
)


class ListFilePathTests(SimpleTestCase):
    """
    Тестирование утилиты поиска абсолютных путей тестовых фотографий.
    """

    def test_paths_exist(self):
        """
        Проверить, что возвращенные пути существуют.
        """
        test_images_dir = os.path.join(temp_root, "gallery", "photos")
        image_paths_list = list_file_paths(test_images_dir)
        self.assertIsInstance(image_paths_list, list)
        for image_path in image_paths_list:
            self.assertTrue(os.path.exists(image_path))


class CalculatePathSizeTests(SimpleTestCase):
    """
    Тесты утилиты определения размера занимаего на диске места.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.files = [
            JpegFileProvider(FAKER).jpeg_file(storage=FS_STORAGE, raw=False)
            for _ in range(3)
        ]
        return super().setUpClass()

    def test_file(self):
        """
        Проверка определения размера файла.
        """
        filepath = FS_STORAGE.abspath(self.files[0])
        filesize = calculate_path_size(filepath)
        self.assertIsInstance(filesize, dict)
        value = filesize.get("value")
        unit = filesize.get("unit")
        message = filesize.get("message")
        self.assertIsInstance(message, str)
        self.assertIsInstance(value, int)
        self.assertIn(str(value), message)
        self.assertIn(unit, message)

    def test_dir(self):
        """
        Проверка определения размера каталога.
        """
        dir_path = os.path.join(FS_STORAGE.root_path, FS_STORAGE.rel_path)
        filesize = calculate_path_size(dir_path)
        self.assertIsInstance(filesize, dict)
