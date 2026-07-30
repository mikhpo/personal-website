"""Миграция данных для заполнения поля exif существующих фотографий."""

import io
import logging

from django.db import migrations
from PIL import Image as pImage
from PIL.ExifTags import TAGS
from PIL.TiffImagePlugin import IFDRational

logger = logging.getLogger(__name__)


def _exif_value_to_json(value: object) -> object:
    """Преобразовать значение EXIF в JSON-совместимый тип.

    Копия функции gallery.utils.exif_value_to_json для самодостаточности миграции.
    """
    if isinstance(value, IFDRational):
        return float(value)
    if isinstance(value, bytes):
        return None
    if isinstance(value, tuple):
        return [_exif_value_to_json(v) for v in value]
    if isinstance(value, (int, float, str)):
        return value
    return str(value)


def extract_exif(image_field: object) -> dict:
    """Извлечь EXIF данные из FieldFile изображения в JSON-совместимый словарь.

    Args:
        image_field: Объект FieldFile (photo.image) с подключённым хранилищем.

    Returns:
        Словарь EXIF данных с человекочитаемыми ключами тегов.
    """
    exif_data: dict = {}
    name = getattr(image_field, "name", None)
    storage = getattr(image_field, "storage", None)
    if not name or not storage or not storage.exists(name):
        return exif_data
    try:
        img_bytes = storage.read_bytes(name)
        with pImage.open(io.BytesIO(img_bytes)) as img:
            if hasattr(img, "_getexif"):
                info = img._getexif()  # noqa: SLF001
                if info:
                    for tag, value in info.items():
                        decoded = TAGS.get(tag, tag)
                        json_value = _exif_value_to_json(value)
                        if json_value is not None:
                            exif_data[decoded] = json_value
    except (FileNotFoundError, PermissionError, OSError):
        logger.exception("Ошибка чтения файла %s при миграции EXIF", name)
    return exif_data


def populate_exif(apps: object, schema_editor: object) -> None:
    """Заполнить поле exif для существующих фотографий.

    Миграция читает каждый файл изображения через хранилище, извлекает EXIF
    данные и сохраняет их в БД. Фотографии с уже заполненным полем пропускаются.
    """
    Photo = apps.get_model("gallery", "Photo")  # type: ignore[attr-defined]
    total = 0
    for photo in Photo.objects.filter(exif__isnull=True).iterator():
        exif_data = extract_exif(photo.image)
        if exif_data:
            photo.exif = exif_data
            photo.save(update_fields=["exif"])
            total += 1
    logger.info("Миграция EXIF: обработано %d фотографий", total)


def reverse_populate(apps: object, schema_editor: object) -> None:
    """Обратная миграция: очистить поле exif у всех фотографий."""
    Photo = apps.get_model("gallery", "Photo")  # type: ignore[attr-defined]
    Photo.objects.exclude(exif__isnull=True).update(exif=None)


class Migration(migrations.Migration):
    dependencies = [
        ("gallery", "0012_photo_exif"),
    ]

    operations = [
        migrations.RunPython(populate_exif, reverse_populate),
    ]
