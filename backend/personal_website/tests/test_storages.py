"""Тесты файловых хранилищ."""

import unittest
from io import BytesIO
from pathlib import Path

import boto3  # type: ignore[import-untyped]
from botocore.client import Config  # type: ignore[import-untyped]
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.test import SimpleTestCase, override_settings

from personal_website.storages import (
    CustomFileSystemStorage,
    CustomS3Storage,
    FakerFileStorageAdapter,
    StorageType,
    select_storage,
)


def is_s3_available() -> bool:
    """Проверить доступность S3 хранилища."""
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.STORAGES["s3"]["OPTIONS"]["access_key"],
            aws_secret_access_key=settings.STORAGES["s3"]["OPTIONS"]["secret_key"],
            endpoint_url=settings.STORAGES["s3"]["OPTIONS"]["endpoint_url"],
            config=Config(signature_version="s3v4"),
        )
        # Попытка получить список бакетов
        s3_client.list_buckets()
    except Exception:  # noqa: BLE001
        return False
    else:
        return True


S3_AVAILABLE = is_s3_available()


class TestFileSystemStorage(SimpleTestCase):
    """Проверка доступа к хранилищу на основе локальной файловой системы."""

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D102
        super().setUpClass()

    def test_storage_dir_location(self) -> None:
        """Проверить, что директория хранилища существует."""
        storage_dir = settings.MEDIA_ROOT
        path_exists = Path(storage_dir).exists()
        self.assertTrue(path_exists)


class TestCustomFileSystemStorage(SimpleTestCase):
    """Тесты для расширенного файлового хранилища."""

    def setUp(self) -> None:  # noqa: D102
        self.storage = CustomFileSystemStorage(location=settings.TEMP_ROOT, base_url="/media/")

    def test_joinpath(self) -> None:
        """Тест объединения путей."""
        result = self.storage.joinpath("path", "to", "file.txt")
        self.assertEqual(result, "path/to/file.txt")

    def test_name(self) -> None:
        """Тест получения имени файла."""
        result = self.storage.name("path/to/file.txt")
        self.assertEqual(result, "file.txt")

    def test_stem(self) -> None:
        """Тест получения имени файла без расширения."""
        result = self.storage.stem("path/to/file.txt")
        self.assertEqual(result, "file")

    def test_suffix(self) -> None:
        """Тест получения расширения файла."""
        result = self.storage.suffix("path/to/file.txt")
        self.assertEqual(result, ".txt")

    def test_with_suffix(self) -> None:
        """Тест изменения расширения файла."""
        result = self.storage.with_suffix("path/to/file.txt", ".jpg")
        self.assertEqual(result, "path/to/file.jpg")

    def test_parent(self) -> None:
        """Тест получения родительского каталога."""
        result = self.storage.parent("path/to/file.txt")
        self.assertEqual(result, "path/to")

    def test_is_absolute(self) -> None:
        """Тест проверки абсолютности пути."""
        result = self.storage.is_absolute("/path/to/file.txt")
        self.assertTrue(result)

        result = self.storage.is_absolute("path/to/file.txt")
        self.assertFalse(result)

    def test_save_and_read_bytes(self) -> None:
        """Тест сохранения и чтения файла."""
        test_content = b"Test content"
        filename = "test_file.txt"

        # Сохранить файл
        saved_name = self.storage.save(filename, ContentFile(test_content))
        self.assertTrue(self.storage.exists(saved_name))

        # Прочитать файл
        content = self.storage.read_bytes(saved_name)
        self.assertEqual(content, test_content)

        # Удалить файл
        self.storage.delete(saved_name)
        self.assertFalse(self.storage.exists(saved_name))


@unittest.skipUnless(S3_AVAILABLE, "S3 storage is not available")
class TestCustomS3Storage(SimpleTestCase):
    """Тесты для S3 хранилища."""

    def setUp(self) -> None:  # noqa: D102
        self.storage = CustomS3Storage(
            bucket_name=settings.STORAGES["s3"]["OPTIONS"]["bucket_name"],
            access_key=settings.STORAGES["s3"]["OPTIONS"]["access_key"],
            secret_key=settings.STORAGES["s3"]["OPTIONS"]["secret_key"],
            region_name=settings.STORAGES["s3"]["OPTIONS"]["region_name"],
            endpoint_url=settings.STORAGES["s3"]["OPTIONS"]["endpoint_url"],
        )

    def test_joinpath(self) -> None:
        """Тест объединения путей для S3."""
        result = self.storage.joinpath("path", "to", "file.txt")
        self.assertEqual(result, "path/to/file.txt")

    def test_name(self) -> None:
        """Тест получения имени файла для S3."""
        result = self.storage.name("path/to/file.txt")
        self.assertEqual(result, "file.txt")

    def test_stem(self) -> None:
        """Тест получения имени файла без расширения для S3."""
        result = self.storage.stem("path/to/file.txt")
        self.assertEqual(result, "file")

    def test_suffix(self) -> None:
        """Тест получения расширения файла для S3."""
        result = self.storage.suffix("path/to/file.txt")
        self.assertEqual(result, ".txt")

    def test_with_suffix(self) -> None:
        """Тест изменения расширения файла для S3."""
        result = self.storage.with_suffix("path/to/file.txt", ".jpg")
        self.assertEqual(result, "path/to/file.jpg")

    def test_parent(self) -> None:
        """Тест получения родительского каталога для S3."""
        result = self.storage.parent("path/to/file.txt")
        self.assertEqual(result, "path/to")

    def test_is_absolute(self) -> None:
        """Тест проверки абсолютности пути для S3."""
        # S3 пути считаются абсолютными
        result = self.storage.is_absolute("s3://bucket/path/to/file.txt")
        self.assertTrue(result)

        # Обычные абсолютные пути тоже
        result = self.storage.is_absolute("/path/to/file.txt")
        self.assertTrue(result)

        # Относительные пути - нет
        result = self.storage.is_absolute("path/to/file.txt")
        self.assertFalse(result)

    def test_save_and_read_bytes(self) -> None:
        """Тест сохранения и чтения файла в S3."""
        test_content = b"Test content for S3"
        filename = "test_s3_file.txt"

        # Сохранить файл
        saved_name = self.storage.save(filename, ContentFile(test_content))
        self.assertTrue(self.storage.exists(saved_name))

        # Прочитать файл
        content = self.storage.read_bytes(saved_name)
        self.assertEqual(content, test_content)

        # Удалить файл
        self.storage.delete(saved_name)
        self.assertFalse(self.storage.exists(saved_name))

    def test_path_returns_s3_uri(self) -> None:
        """Тест возврата S3 URI для файла."""
        filename = "test_file.txt"
        path = self.storage.path(filename)
        self.assertTrue(path.startswith("s3://"))
        self.assertIn(self.storage.bucket_name, path)

    def test_save_document(self) -> None:
        """Тест сохранения документа через функцию."""
        filename = "test_document.txt"

        def write_func(stream: BytesIO) -> None:
            stream.write(b"Document content")

        saved_name = self.storage.save_document(filename, write_func)
        self.assertTrue(self.storage.exists(saved_name))

        # Прочитать и проверить содержимое
        content = self.storage.read_bytes(saved_name)
        self.assertEqual(content, b"Document content")

        # Удалить файл
        self.storage.delete(saved_name)

    def test_save(self) -> None:
        """Тест сохранения файла в S3."""
        test_content = b"Test content for S3 save method"
        filename = "test_save_file.txt"
        saved_name = self.storage.save(filename, test_content)
        self.assertTrue(self.storage.exists(saved_name))
        content = self.storage.read_bytes(saved_name)
        self.assertEqual(content, test_content)
        self.storage.delete(saved_name)
        self.assertFalse(self.storage.exists(saved_name))

    def test_save_overwrites_existing_file(self) -> None:
        """Тест перезаписи существующего файла в S3."""
        filename = "test_overwrite_file.txt"
        original_content = b"Original content"
        updated_content = b"Updated content"

        # Сохранить исходный файл
        saved_name = self.storage.save(filename, ContentFile(original_content))
        self.assertTrue(self.storage.exists(saved_name))

        # Прочитать и проверить исходное содержимое
        content = self.storage.read_bytes(saved_name)
        self.assertEqual(content, original_content)

        # Перезаписать файл новым содержимым
        self.storage.save(filename, ContentFile(updated_content))

        # Прочитать и проверить обновленное содержимое
        content = self.storage.read_bytes(saved_name)
        self.assertEqual(content, updated_content)

        # Удалить файл
        self.storage.delete(saved_name)
        self.assertFalse(self.storage.exists(saved_name))

    def test_mkdir_is_noop(self) -> None:
        """Тест что mkdir для S3 является no-op операцией."""
        # Не должно вызывать ошибок
        self.storage.mkdir("test/directory")

    def test_is_dir_always_false(self) -> None:
        """Тест что is_dir для S3 всегда возвращает False."""
        result = self.storage.is_dir("any/path")
        self.assertFalse(result)

    def test_rmdir_is_noop(self) -> None:
        """Тест что rmdir для S3 является no-op операцией."""
        # Не должно вызывать ошибок
        self.storage.rmdir("test/directory")


class TestFakerFileStorageAdapter(SimpleTestCase):
    """Тесты для адаптера FakerFileStorageAdapter."""

    def setUp(self) -> None:
        """Настроить тестовое хранилище."""
        self.faker_storage = FakerFileStorageAdapter()

    def test_generate_filename(self) -> None:
        """Тест генерации имени файла."""
        filename = self.faker_storage.generate_filename(extension="txt", prefix="test_")
        self.assertTrue(filename.endswith(".txt"))
        self.assertIn("test_", filename)

    def test_write_text(self) -> None:
        """Тест записи текстовых данных в файл."""
        filename = "test_write_text.txt"
        data = "Тестовые текстовые данные"
        bytes_written = self.faker_storage.write_text(filename, data)
        self.assertEqual(bytes_written, len(data.encode("utf-8")))
        self.assertTrue(self.faker_storage.exists(filename))
        self.faker_storage.unlink(filename)
        self.assertFalse(self.faker_storage.exists(filename))

    def test_write_bytes(self) -> None:
        """Тест записи байтовых данных в файл."""
        filename = "test_write_bytes.txt"
        data = b"Test binary data"
        bytes_written = self.faker_storage.write_bytes(filename, data)
        self.assertEqual(bytes_written, len(data))
        self.assertTrue(self.faker_storage.exists(filename))
        self.faker_storage.unlink(filename)
        self.assertFalse(self.faker_storage.exists(filename))

    def test_exists(self) -> None:
        """Тест проверки существования файла."""
        filename = "test_exists.txt"
        data = b"Test data"
        self.assertFalse(self.faker_storage.exists(filename))
        self.faker_storage.write_bytes(filename, data)
        self.assertTrue(self.faker_storage.exists(filename))
        self.faker_storage.unlink(filename)
        self.assertFalse(self.faker_storage.exists(filename))

    def test_abspath(self) -> None:
        """Тест получения абсолютного пути к файлу."""
        filename = "test_abspath.txt"
        abs_path = self.faker_storage.abspath(filename)
        self.assertTrue(abs_path.endswith(filename))

    def test_relpath(self) -> None:
        """Тест получения относительного пути к файлу."""
        filename = "test_relpath.txt"
        rel_path = self.faker_storage.relpath(filename)
        self.assertEqual(rel_path, filename)

    def test_read(self) -> None:
        """Тест чтения данных из файла."""
        filename = "test_read.txt"
        data = b"Test read data"
        self.faker_storage.write_bytes(filename, data)
        read_data = self.faker_storage.read(filename)
        self.assertEqual(read_data, data)
        self.faker_storage.unlink(filename)

    def test_delete(self) -> None:
        """Тест удаления файла."""
        filename = "test_delete.txt"
        data = b"Test delete data"
        self.faker_storage.write_bytes(filename, data)
        self.assertTrue(self.faker_storage.exists(filename))
        self.faker_storage.delete(filename)
        self.assertFalse(self.faker_storage.exists(filename))

    def test_unlink(self) -> None:
        """Тест удаления файла через unlink."""
        filename = "test_unlink.txt"
        data = b"Test unlink data"
        self.faker_storage.write_bytes(filename, data)
        self.assertTrue(self.faker_storage.exists(filename))
        self.faker_storage.unlink(filename)
        self.assertFalse(self.faker_storage.exists(filename))

    def test_mkdir(self) -> None:
        """Тест создания директории."""
        directory = "test_directory"

        # Так как создания директории от конкретной реализации,
        # просто проверяем, что метод не вызвал ошибок
        self.faker_storage.mkdir(directory)


class TestSelectStorage(SimpleTestCase):
    """Тесты механизма выбора хранилища."""

    def test_select_storage_returns_test_storage_in_test_mode_without_s3(self) -> None:
        """В тестовом режиме без S3 select_storage возвращает тестовое хранилище."""
        with override_settings(TEST=True, STORAGE_TYPE="filesystem"):
            storage: StorageType = select_storage()
            self.assertIsInstance(storage, FileSystemStorage)
            self.assertEqual(Path(storage.location).name, "temp")

    @override_settings(TEST=True, STORAGE_TYPE="s3")
    def test_select_storage_returns_s3_storage_in_test_mode_with_s3_type(self) -> None:
        """В тестовом режиме с STORAGE_TYPE = 's3' select_storage возвращает S3 хранилище."""
        storage: StorageType = select_storage()
        self.assertIsInstance(storage, CustomS3Storage)

    @override_settings(TEST=False, STORAGE_TYPE="s3")
    def test_select_storage_returns_s3_storage_when_storage_type_is_s3(self) -> None:
        """Когда STORAGE_TYPE = 's3', select_storage возвращает S3 хранилище."""
        storage: StorageType = select_storage()
        self.assertIsInstance(storage, CustomS3Storage)

    @override_settings(TEST=False, STORAGE_TYPE="filesystem")
    def test_select_storage_returns_filesystem_storage_by_default(self) -> None:
        """По умолчанию select_storage возвращает файловое хранилище."""
        storage: StorageType = select_storage()
        self.assertIsInstance(storage, FileSystemStorage)
        self.assertNotEqual(Path(storage.location).name, "temp")
