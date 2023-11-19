import os
from pathlib import Path

from config.storages import select_storage

from .apps import GalleryConfig


def photo_image_upload_path(instance, filename):
    """
    Определение пути загрузки фотографий. Фотографии загружаются в папку своего альбома.
    """
    app_name = GalleryConfig.name
    album = instance.album
    return f"{app_name}/albums/{album.pk}/photos/{filename}"


def photo_image_upload_full_path(photo, filename: str) -> str:
    """
    Получить полный путь загрузки файла.
    """
    storage = select_storage()
    storage_dir = storage.location
    relative_path = photo_image_upload_path(photo, filename)
    full_path = os.path.join(storage_dir, relative_path)
    return full_path


def move_photo_image(photo, source_path: str):
    """
    Переместить изображение фотографии с адреса источника по новому адресу,
    определенному в соответствии с внутренней бизнес-логикой модели.
    Возвращает полный адрес, по которому было перемещено изображение.
    """
    file_name = Path(source_path).name
    new_path = photo_image_upload_full_path(photo, file_name)
    Path(new_path).parent.mkdir(parents=True, exist_ok=True)
    Path(source_path).replace(new_path)
    return new_path
