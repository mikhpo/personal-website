"""Фоновые задачи приложения галереи."""

from django.tasks import task

from gallery.models import Photo


@task
def generate_photo_images(photo_pk: int) -> None:
    """Сгенерировать миниатюру и превью фотографии.

    Задача выполняется воркером huey после загрузки или изменения
    фотографии. Генерация идемпотентна: кэш-файлы ImageKit
    перезаписываются. Если фотография удалена до выполнения задачи,
    генерация пропускается.
    """
    try:
        photo = Photo.objects.get(pk=photo_pk)
    except Photo.DoesNotExist:
        return
    photo.image_thumbnail.generate(force=True)
    photo.image_preview.generate(force=True)
