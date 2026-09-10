"""Сигналы приложения галереи."""

import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from gallery.models import Photo
from gallery.tasks import generate_photo_images

logger = logging.getLogger(__name__)


def _enqueue_photo_images(photo_pk: int) -> None:
    """Поставить задачу генерации миниатюр и превью фотографии.

    Отказ постановки (недоступная очередь, отсутствие таблиц) не прерывает
    выполнение: отказ записывается в журнал, а миниатюры будут
    сгенерированы при первом обращении к ним (JustInTime).
    """
    try:
        generate_photo_images.enqueue(photo_pk)
    except Exception:
        logger.exception("Постановка задачи генерации миниатюр не удалась для фотографии %s", photo_pk)


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

    Постановка отложена до коммита транзакции: воркер не видит
    незакоммиченные строки, а отказ записи в очередь не прерывает
    выполняющийся запрос и не влияет на остальные on_commit callbacks.
    """
    if update_fields is not None and not set(update_fields) & {"image", "album"}:
        return
    transaction.on_commit(lambda: _enqueue_photo_images(instance.pk))
