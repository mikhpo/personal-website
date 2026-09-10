"""Фоновые задачи приложения галереи."""

from django.tasks import task
from imagekit.cachefiles import ImageCacheFile

from gallery.models import Photo


def _is_fresh(cachefile: ImageCacheFile) -> bool:
    """Определить, что кэш-файл производной версии существует и новее исходника.

    Имя кэш-файла зависит только от имени исходника и параметров
    спецификации, поэтому замена исходника под тем же именем оставляет
    прежнее имя кэша - свежесть определяется сравнением времени изменения.
    """
    storage = cachefile.storage
    source_name = cachefile.generator.source.name
    if not storage.exists(cachefile.name) or not storage.exists(source_name):
        return False
    cache_mtime = storage.get_modified_time(cachefile.name)
    source_mtime = storage.get_modified_time(source_name)
    return cache_mtime >= source_mtime


@task
def generate_photo_images(photo_pk: int) -> None:
    """Сгенерировать миниатюру и превью фотографии.

    Задача выполняется воркером huey после загрузки или изменения
    фотографии. Актуальный кэш не перегенерируется: правки названия
    или описания фотографии, вызывающие полное сохранение, не создают
    работу воркеру. Замена изображения под тем же именем файла
    перегенерирует кэш принудительно. Если фотография удалена
    до выполнения задачи, генерация пропускается.
    """
    try:
        photo = Photo.objects.get(pk=photo_pk)
    except Photo.DoesNotExist:
        return
    for cachefile in (photo.image_thumbnail, photo.image_preview):
        if not _is_fresh(cachefile):
            cachefile.generate(force=True)
