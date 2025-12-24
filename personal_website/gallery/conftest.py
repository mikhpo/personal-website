"""Фикстуры тестов галереи."""

from collections.abc import Generator
from typing import Any

import pytest
from faker import Faker
from faker_file.providers.jpeg_file import JpegFileProvider  # type:ignore[import-untyped]

from gallery.factories import ExifDataFactory
from gallery.utils import write_exif
from personal_website.storages import StorageType, select_storage


@pytest.fixture(scope="session", autouse=True)
def manage_test_images() -> Generator[str, Any, None]:
    """Управление тестовыми изображениями для запуска тестов галереи.

    Создает тестовые изображения перед выполнением тестов.
    Удаляет тестоыве изображения после завершения выполнения тестов.
    """
    # Получить адрес папки для тестовых изображений.
    relative_path = "gallery/photos"

    # Создать папку для тестовых изображений перед запуском тестов галереи.
    storage: StorageType = select_storage()

    fake = Faker()

    # Создать фотографии для альбома Тосканы.
    for i in range(3):
        file_name = f"Tuscany {i}.jpg"
        file_path = f"{relative_path}/{file_name}"
        jpeg_file = JpegFileProvider(fake).jpeg_file(raw=True)
        storage.save(file_path, jpeg_file)
        exif_data = ExifDataFactory()
        write_exif(file_path, exif_data)

    # Создать фотографии для альбома Лангтанг.
    for i in range(2):
        file_name = f"Langtang {i}.jpg"
        file_path = f"{relative_path}/{file_name}"
        jpeg_file = JpegFileProvider(fake).jpeg_file(raw=True)
        storage.save(file_path, jpeg_file)
        exif_data = ExifDataFactory()
        write_exif(file_path, exif_data)

    # Передать адрес временной папки как фикстуру для тестов.
    yield relative_path

    # Удалить временную папку со всем содержимым.
    storage.rmtree(relative_path, ignore_errors=True)
