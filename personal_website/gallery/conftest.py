"""Фикстуры тестов галереи."""

import os
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from django.conf import settings
from faker import Faker
from faker_file.providers.jpeg_file import JpegFileProvider  # type: ignore[import-untyped]
from faker_file.storages.filesystem import FileSystemStorage  # type: ignore[import-untyped]

from gallery.factories import ExifDataFactory
from gallery.utils import write_exif


@pytest.fixture(scope="session", autouse=True)
def manage_test_images() -> Generator[str, Any, None]:
    """Управление тестовыми изображениями для запуска тестов галереи.

    Создает тестовые изображения перед выполнением тестов.
    Удаляет тестоыве изображения после завершения выполнения тестов.
    """
    # Получить адрес папки для тестовых изображений.

    root_path = os.getenv("TEMP_ROOT", default=Path(settings.PROJECT_DIR) / "temp")
    relative_path = "gallery/photos"
    test_images_dir = Path(root_path) / relative_path

    # Создать папку для тестовых изображений перед запуском тестов галереи.
    Path(test_images_dir).mkdir(parents=True, exist_ok=True)

    fake = Faker()
    gallery_storage = FileSystemStorage(root_path=root_path, rel_path=relative_path)

    # Создать фотографии для альбома Тосканы.
    for i in range(3):
        jpeg_file = JpegFileProvider(fake).jpeg_file(storage=gallery_storage, basename=f"Tuscany {i}", raw=False)
        jpeg_file_path = gallery_storage.abspath(jpeg_file)
        exif_data = ExifDataFactory()
        write_exif(jpeg_file_path, exif_data)

    # Создать фотографии для альбома Лангтанг.
    for i in range(2):
        jpeg_file = JpegFileProvider(fake).jpeg_file(storage=gallery_storage, basename=f"Langtang {i}", raw=False)
        jpeg_file_path = gallery_storage.abspath(jpeg_file)
        exif_data = ExifDataFactory()
        write_exif(jpeg_file_path, exif_data)

    # Передать адрес временной папки как фикстуру для тестов.
    yield str(test_images_dir)

    # Удалить временную папку со всем содержимым.
    shutil.rmtree(test_images_dir, ignore_errors=True)
