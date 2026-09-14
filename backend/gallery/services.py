"""Сервисные операции пакетной загрузки фотографий и превью для вставок."""

import logging
from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING

from django.conf import settings
from imagekit.processors import ResizeToFit
from PIL import Image, ImageOps, UnidentifiedImageError

from gallery.models import Album, Photo

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(settings.PROJECT_NAME)

# Расширения файлов превью для вставок по форматам исходников;
# превью сохраняется в формате исходного изображения. Ключи - канонические
# имена форматов PIL (значение Image.open().format): для любого JPEG-файла,
# независимо от расширения (.jpg, .jpeg, .jfif), PIL возвращает "JPEG".
EMBED_PREVIEW_EXTENSIONS: dict[str, str] = {
    "JPEG": "jpg",
    "PNG": "png",
    "GIF": "gif",
    "TIFF": "tif",
    "WEBP": "webp",
}

# Форматы, для которых при перекодировании задается качество сжатия.
QUALITY_FORMATS: set[str] = {"JPEG", "WEBP"}


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


def find_embed_preview(photo: Photo, size: int) -> str | None:
    """Найти существующий файл превью нужного размера в каталоге хранилища.

    Расширение файла определяется форматом исходного изображения, поэтому
    поиск выполняется по префиксу имени без учета расширения. Отсутствие
    каталога означает, что превью еще не запрашивались.
    """
    directory = photo.embed_preview_dir()
    try:
        files, _ = photo.image.storage.listdir(directory)
    except OSError:
        return None
    for filename in files:
        if filename.startswith(f"{size}."):
            return f"{directory}/{filename}"
    return None


def embed_preview_is_fresh(photo: Photo, embed_name: str) -> bool:
    """Определить, что файл превью для вставки существует и новее исходного изображения.

    Сравнение времени изменения повторяет логику проверки кэша миниатюр
    (gallery.tasks._is_fresh): замена исходника под тем же именем файла
    делает существующее превью устаревшим и требует перегенерации.
    """
    storage = photo.image.storage
    source_name = photo.image.name
    if not source_name or not storage.exists(source_name) or not storage.exists(embed_name):
        return False
    return storage.get_modified_time(embed_name) >= storage.get_modified_time(source_name)


def generate_embed_preview(photo: Photo, size: int, previous_name: str | None = None) -> str:
    """Сгенерировать превью фотографии для вставки нужного размера в формате исходника.

    Пропорции сохраняются автоматически: вписывание выполняется по наибольшей
    стороне (ResizeToFit). Ориентация из EXIF переносится в пикселы, поскольку
    перекодированный файл не сохраняет метаданные исходника. Анимированные
    исходники дают статичное превью первого кадра. Превью прежнего формата
    (если формат исходника изменился) удаляется.

    Returns:
        Имя сохраненного файла превью в хранилище.
    """
    storage = photo.image.storage
    image_bytes = storage.read_bytes(photo.image.name)
    with Image.open(BytesIO(image_bytes)) as img:
        source_format = img.format or "JPEG"
        oriented = ImageOps.exif_transpose(img)
        resized = ResizeToFit(width=size, height=size).process(oriented)
        options: dict = {"quality": settings.GALLERY_RESIZE_QUALITY} if source_format in QUALITY_FORMATS else {}
        extension = EMBED_PREVIEW_EXTENSIONS.get(source_format, source_format.lower())
        embed_name = f"{photo.embed_preview_dir()}/{size}.{extension}"
        with BytesIO() as buffer:
            resized.save(buffer, format=source_format, **options)
            storage.save(embed_name, buffer.getvalue())
    if previous_name and previous_name != embed_name:
        storage.delete(previous_name)
    return embed_name


def ensure_embed_preview(photo: Photo, size: int) -> str:
    """Вернуть имя файла превью для вставки, при отсутствии или устаревании сгенерировать.

    Превью создается в формате исходного изображения: исходник PNG дает PNG,
    JPEG - JPEG. Ссылки на превью содержат расширение актуального формата.

    Raises:
        FileNotFoundError: файл исходного изображения отсутствует в хранилище.
    """
    source_name = photo.image.name
    if not source_name or not photo.image.storage.exists(source_name):
        raise FileNotFoundError(source_name or f"У фотографии {photo.pk} не указано изображение")
    existing_name = find_embed_preview(photo, size)
    if existing_name and embed_preview_is_fresh(photo, existing_name):
        return existing_name
    return generate_embed_preview(photo, size, existing_name)
