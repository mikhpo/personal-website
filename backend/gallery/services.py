"""Сервисные операции пакетной загрузки фотографий в альбом."""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.conf import settings
from PIL import Image, UnidentifiedImageError

from gallery.models import Album, Photo

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(settings.PROJECT_NAME)


@dataclass(frozen=True)
class PhotoUploadResult:
    """Результат обработки одного файла при пакетной загрузке."""

    filename: str
    photo: Photo | None = None
    error: Exception | None = None

    @property
    def success(self) -> bool:
        """Файл обработан успешно, фотография создана."""
        return self.photo is not None and self.error is None


def upload_photos_to_album(album: Album, files: "Sequence[UploadedFile]") -> list[PhotoUploadResult]:
    """Верифицировать и создать фотографию для каждого загруженного файла.

    Невалидный файл или сбой сохранения не прерывают обработку остальных
    файлов: каждый файл дает собственный результат с созданной фотографией
    или ошибкой.
    """
    results: list[PhotoUploadResult] = []
    for file in files:
        try:
            image = Image.open(file)
            image.verify()
            photo = Photo.objects.create(image=file, album=album)
            results.append(PhotoUploadResult(filename=file.name or "", photo=photo))
            logger.debug(f"Загружена фотография {file} в альбом {album}")
        except UnidentifiedImageError as error:  # noqa: PERF203
            logger.exception(f'Загруженный файл "{file}" не является изображением')
            results.append(PhotoUploadResult(filename=file.name or "", error=error))
        except Exception as error:
            message = f'Ошибка загрузки фотографии в альбом "{album}": "{error}"'
            logger.exception(message)
            results.append(PhotoUploadResult(filename=file.name or "", error=error))

    uploaded = sum(1 for result in results if result.success)
    if uploaded:
        logger.info(f"Загружено {uploaded} фотографий в альбом {album.name}")
    return results


def upload_error_message(result: PhotoUploadResult, album: Album) -> str:
    """Сформировать текст сообщения об ошибке загрузки одного файла."""
    if isinstance(result.error, UnidentifiedImageError):
        return f'Загруженный файл "{result.filename}" не является изображением'
    return f'Ошибка загрузки фотографии в альбом "{album}": "{result.error}"'
