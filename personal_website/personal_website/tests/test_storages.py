"""Тесты файловых хранилищ."""

from io import BytesIO
from pathlib import Path

import pytest
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.test import SimpleTestCase

from personal_website.storages import CustomFileSystemStorage, CustomS3Storage, select_storage


def is_s3_available() -> bool:
    """Проверить доступность S3 хранилища."""
    try:
        import boto3  # type: ignore[import-untyped]
        from botocore.client import Config  # type: ignore[import-untyped]

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


class CustomFileSystemStorageTests(SimpleTestCase):
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


@pytest.mark.skipif(not S3_AVAILABLE, reason="S3 storage is not available")
class CustomS3StorageTests(SimpleTestCase):
    """Тесты для S3 хранилища."""

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D102
        super().setUpClass()
        # Создать тестовый бакет, если он не существует
        import boto3  # type: ignore[import-untyped]
        from botocore.client import Config  # type: ignore[import-untyped]

        cls.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.STORAGES["s3"]["OPTIONS"]["access_key"],
            aws_secret_access_key=settings.STORAGES["s3"]["OPTIONS"]["secret_key"],
            endpoint_url=settings.STORAGES["s3"]["OPTIONS"]["endpoint_url"],
            config=Config(signature_version="s3v4"),
        )

        bucket_name = settings.STORAGES["s3"]["OPTIONS"]["bucket_name"]
        try:  # noqa: SIM105
            cls.s3_client.create_bucket(Bucket=bucket_name)
        except Exception:  # noqa: BLE001, S110
            # Бакет уже существует
            pass

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


class SelectStorageTests(SimpleTestCase):
    """Тесты механизма выбора хранилища."""

    def test_select_storage_returns_test_storage_in_test_mode(self) -> None:
        """В тестовом режиме select_storage возвращает тестовое хранилище."""
        storage = select_storage()
        self.assertIsInstance(storage, FileSystemStorage)
        # В тестовом режиме всегда используется test хранилище
        self.assertTrue(settings.TEST)
        self.assertEqual(Path(storage.location).name, "temp")
