"""Вспомогательные функции галереи."""

from io import BytesIO

from django.db.models import Model
from faker import Faker
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS, Base

from gallery.apps import GalleryConfig
from gallery.schemas import ExifData
from personal_website.storages import StorageType, select_storage

fake = Faker(locale="ru_RU")
storage: StorageType = select_storage()


def photo_image_upload_path(instance: Model, filename: str) -> str:
    """Определение пути загрузки фотографий. Фотографии загружаются в папку своего альбома."""
    return f"{GalleryConfig.name}/albums/{instance.album.pk}/photos/{filename}"


def photo_image_upload_full_path(photo: Model, filename: str) -> str:
    """Получить полный путь загрузки файла."""
    relative_path = photo_image_upload_path(photo, filename)
    return storage.path(relative_path)


def move_photo_image(photo: Model, source_path: str) -> str:
    """
    Переместить изображение фотографии с адреса источника по адресу,
    определенному в соответствии с внутренней бизнес-логикой модели.

    Returns:
        str: полный адрес, по которому было перемещено изображение.
    """
    file_name = storage.name(source_path)
    new_path = photo_image_upload_full_path(photo, file_name)
    parent_dir = storage.parent(new_path)
    storage.mkdir(parent_dir, parents=True, exist_ok=True)
    storage.replace(source_path, new_path)
    return new_path


def is_image(file: str) -> bool:
    """Проверяет, является ли файл изображением.

    Returns:
        bool:
            - Если файл является изображением, то True.
            - Если файл не является изображением, то False.
    """
    try:
        file_content = storage.read_bytes(str(file))
        file_bytes = BytesIO(file_content)
        image = Image.open(file_bytes)
        image.verify()
    except UnidentifiedImageError:
        return False
    else:
        return True


def _open_image_for_exif(image: str) -> Image.Image:
    """Открывает изображение для работы с EXIF данными, используя storage при необходимости."""
    file_content = storage.read_bytes(image)
    image_bytes = BytesIO(file_content)
    return Image.open(image_bytes)


def read_exif(image: str) -> ExifData:
    """Прочитать данные EXIF изображения.

    Args:
        image (str): Изображение, EXIF данные которого необходимо прочитать.

    Returns:
        ExifData: Данные EXIF (модель Pydantic).
    """
    exif_data = {}
    with _open_image_for_exif(image) as img:
        if exif := img.getexif():
            for tag, value in exif.items():
                decoded = TAGS.get(tag, tag)
                exif_data[decoded] = value
    return ExifData.model_validate(exif_data)


def write_exif(image: str, exif_data: ExifData) -> None:
    """Записать данные EXIF в изображение.

    Args:
        image (str): Путь к изображению, EXIF данные которого необходимо записать.
        exif_data (ExifData): объект модели Pydantic, содержащий все данные EXIF.
    """
    file_content = storage.read_bytes(image)
    image_bytes = BytesIO(file_content)
    with Image.open(image_bytes) as img:
        exif = img.getexif()

        # Обновляем EXIF данные
        for key, value in exif_data.model_dump(mode="json", by_alias=True).items():
            exif_tag = Base[key]
            exif.__setitem__(exif_tag, value)

        # Сохраняем изображение обратно в байты с новыми EXIF данными
        with BytesIO() as output:
            img.save(output, format=img.format, exif=exif.tobytes())
            storage.save(image, output.getvalue())
