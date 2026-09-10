"""Сигналы приложения галереи."""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from gallery.models import Photo
from gallery.tasks import generate_photo_images

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Photo)
def enqueue_photo_image_generation(
    sender: type[Photo],
    instance: Photo,
    update_fields: frozenset[str] | None,
    **kwargs: object,
) -> None:
    """Поставить задачу генерации миниатюры и превью после сохранения фотографии.

    Задача ставится в очередь при создании фотографии, замене изображения
    и смене альбома с перемещением файла в хранилище. Частичные сохранения
    прочих полей, например EXIF и taken_at, задачу не порождают. Дубликаты
    задач безопасны: генерация идемпотентна и перезаписывает кэш-файлы.

    Отказ постановки (недоступная очередь, отсутствие таблиц) не прерывает
    сохранение фотографии и извлечение EXIF: задача записывается в журнал,
    а миниатюры будут сгенерированы при первом обращении к ним.
    """
    if update_fields is not None and not set(update_fields) & {"image", "album"}:
        return
    try:
        generate_photo_images.enqueue(instance.pk)
    except Exception:
        logger.exception("Постановка задачи генерации миниатюр не удалась для фотографии %s", instance.pk)
