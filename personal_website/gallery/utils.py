"""Вспомогательные функции галереи."""
from pathlib import Path
from typing import Any

from django.db.models import Model
from PIL import Image, UnidentifiedImageError

from gallery.apps import GalleryConfig
from personal_website.storages import select_storage


def photo_image_upload_path(instance: Model, filename: str) -> str:
    """Определение пути загрузки фотографий. Фотографии загружаются в папку своего альбома."""
    return f"{GalleryConfig.name}/albums/{instance.album.pk}/photos/{filename}"


def photo_image_upload_full_path(photo: Model, filename: str) -> str:
    """Получить полный путь загрузки файла."""
    storage = select_storage()
    storage_dir = storage.location
    relative_path = photo_image_upload_path(photo, filename)
    full_path = Path(storage_dir) / relative_path
    return str(full_path)


def move_photo_image(photo: Model, source_path: str) -> str:
    """
    Переместить изображение фотографии с адреса источника по адресу,
    определенному в соответствии с внутренней бизнес-логикой модели.
    Возвращает полный адрес, по которому было перемещено изображение.
    """
    file_name = Path(source_path).name
    new_path = photo_image_upload_full_path(photo, file_name)
    Path(new_path).parent.mkdir(parents=True, exist_ok=True)
    Path(source_path).replace(new_path)
    return new_path


def is_image(file: Any) -> bool:  # noqa: ANN401
    """Проверяет, является ли файл изображением.

    Returns:
        bool:
            - Если файл является изображением, то True.
            - Если файл не является изображением, то False.
    """
    try:
        image = Image.open(file)
        image.verify()
    except UnidentifiedImageError:
        return False
    else:
        return True
