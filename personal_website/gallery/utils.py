"""Вспомогательные функции галереи."""

from io import BytesIO
from pathlib import Path
from typing import Any

from django.db.models import Model
from faker import Faker
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS, Base

from gallery.apps import GalleryConfig
from gallery.schemas import ExifData
from personal_website.storages import select_storage

fake = Faker(locale="ru_RU")


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

    Returns:
        str: полный адрес, по которому было перемещено изображение.
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


def read_exif(image: str | Path | BytesIO) -> ExifData:
    """Прочитать данные EXIF изображения.

    Args:
        image (str | Path | BytesIO): Изображение, EXIF данные которого необходимо прочитать.

    Returns:
        ExifData: Словарь с данными EXIF (модель Pydantic).
    """
    exif_data = {}
    with Image.open(image) as img:
        if exif := img.getexif():
            for tag, value in exif.items():
                decoded = TAGS.get(tag, tag)
                exif_data[decoded] = value
        img.close()
    return ExifData.model_validate(exif_data)


def write_exif(image: str | Path | BytesIO, exif_data: ExifData) -> None:
    """Записать данные EXIF в изображение.

    Args:
        image (str | Path | BytesIO): Изображение, EXIF данные которого необходимо записать.
        exif_data (ExifData): объект модели Pydantic, содержащий все данные EXIF.
    """
    exif_dict = exif_data.model_dump(mode="json", by_alias=True)
    with Image.open(image) as img:
        exif = img.getexif()
        for key, value in exif_dict.items():
            exif_tag = Base[key]
            exif.__setitem__(exif_tag, value)
        img.save(image, exif=exif)
