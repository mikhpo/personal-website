"""Тесты вспомогательных функций для работы с файлами и файловой системой."""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase
from faker import Faker
from faker_file.providers.jpeg_file import JpegFileProvider  # type: ignore[import-untyped]

from personal_website.storages import FakerFileStorageAdapter
from personal_website.utils import calculate_path_size, list_file_paths

FAKER = Faker()
FS_STORAGE = FakerFileStorageAdapter(
    root_path=settings.TEMP_ROOT,
    rel_path=Path(__file__).resolve().stem,
)


class ListFilePathTests(SimpleTestCase):
    """Тестирование утилиты поиска абсолютных путей тестовых фотографий."""

    @classmethod
    def setUpClass(cls) -> None:
        """Создать тестовую директорию с изображениями."""
        super().setUpClass()
        cls.test_images_dir = Path(settings.TEMP_ROOT) / "test_list_file_paths"
        cls.test_images_dir.mkdir(parents=True, exist_ok=True)

        # Создать несколько тестовых файлов
        fs_storage = FakerFileStorageAdapter(
            root_path=settings.TEMP_ROOT,
            rel_path="test_list_file_paths",
        )
        cls.files = [JpegFileProvider(FAKER).jpeg_file(storage=fs_storage, raw=False) for _ in range(3)]

    def test_paths_exist(self) -> None:
        """Проверить, что возвращенные пути существуют."""
        image_paths_list = list_file_paths(self.test_images_dir)
        self.assertIsInstance(image_paths_list, list)
        self.assertEqual(len(image_paths_list), 3)
        for image_path in image_paths_list:
            image_exists = Path(image_path).exists()
            self.assertTrue(image_exists)


class CalculatePathSizeTests(SimpleTestCase):
    """Тесты утилиты определения размера занимаего на диске места."""

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D102
        cls.files = [JpegFileProvider(FAKER).jpeg_file(storage=FS_STORAGE, raw=False) for _ in range(3)]
        return super().setUpClass()

    def test_file(self) -> None:
        """Проверка определения размера файла."""
        filepath = FS_STORAGE.abspath(self.files[0])
        filesize = calculate_path_size(filepath)
        self.assertIsInstance(filesize, dict)
        if filesize:
            value = filesize["value"]
            unit = filesize["unit"]
            message = filesize["message"]
            self.assertIsInstance(message, str)
            self.assertIsInstance(value, int)
            self.assertIn(str(value), message)
            self.assertIn(unit, message)

    def test_dir(self) -> None:
        """Проверка определения размера каталога."""
        dir_path = Path(FS_STORAGE.root_path) / FS_STORAGE.rel_path
        filesize = calculate_path_size(dir_path)
        self.assertIsInstance(filesize, dict)
