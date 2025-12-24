"""Тесты вспомогательных функций для работы с файлами и файловой системой."""

from django.test import SimpleTestCase
from faker import Faker

from personal_website.storages import select_storage
from personal_website.utils import list_file_paths

FAKER = Faker()
storage = select_storage()


class ListFilePathTests(SimpleTestCase):
    """Тестирование утилиты поиска абсолютных путей тестовых фотографий."""

    def test_paths_exist(self) -> None:
        """Проверить, что возвращенные пути существуют."""
        # Создаем тестовую директорию в хранилище
        test_dir = "test_list_file_paths"
        storage.mkdir(test_dir, parents=True, exist_ok=True)

        # Создаем несколько тестовых файлов напрямую через хранилище
        file_paths = []
        for i in range(3):
            file_name = f"test_file_{i}.jpg"
            file_path = storage.joinpath(test_dir, file_name)
            # Создаем пустой файл
            storage.save(file_path, b"test content")
            file_paths.append(file_path)

        # Вызываем функцию
        image_paths_list = list_file_paths(test_dir)

        # Проверяем результаты
        self.assertIsInstance(image_paths_list, list)
        self.assertEqual(len(image_paths_list), 3)
        for image_path in image_paths_list:
            # Проверяем, что путь существует в хранилище
            self.assertTrue(storage.exists(image_path))

        # Очищаем тестовые файлы
        storage.rmtree(test_dir, ignore_errors=True)

    def test_empty_directory(self) -> None:
        """Проверить поведение функции для пустой директории."""
        # Создаем пустую директорию
        test_dir = "test_empty_directory"
        storage.mkdir(test_dir, parents=True, exist_ok=True)

        # Вызываем функцию
        result = list_file_paths(test_dir)

        # Проверяем, что возвращается пустой список
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

        # Очищаем тестовые файлы
        storage.rmtree(test_dir, ignore_errors=True)

    def test_nonexistent_directory(self) -> None:
        """Проверить поведение функции для несуществующей директории."""
        # Вызываем функцию с несуществующим путем
        result = list_file_paths("nonexistent_directory")

        # Проверяем, что возвращается пустой список
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_with_subdirectories(self) -> None:
        """Проверить поведение функции с подкаталогами."""
        # Создаем тестовую директорию
        test_dir = "test_with_subdirs"
        storage.mkdir(test_dir, parents=True, exist_ok=True)

        # Создаем файлы и подкаталоги
        file1 = storage.joinpath(test_dir, "file1.txt")
        storage.save(file1, b"test content 1")

        file2 = storage.joinpath(test_dir, "file2.txt")
        storage.save(file2, b"test content 2")

        # Создаем подкаталог
        subdir = storage.joinpath(test_dir, "subdir")
        storage.mkdir(subdir, parents=True, exist_ok=True)

        # Вызываем функцию
        result = list_file_paths(test_dir)

        # Проверяем, что возвращаются только пути к файлам, а не подкаталогам
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        # Проверяем, что возвращенные пути существуют
        for path in result:
            self.assertTrue(storage.exists(path))
            # Проверяем, что это файл, а не директория
            self.assertFalse(storage.is_dir(path))

        # Очищаем тестовые файлы
        storage.rmtree(test_dir, ignore_errors=True)
