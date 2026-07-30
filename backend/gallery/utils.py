"""Вспомогательные функции галереи."""

from datetime import datetime
from io import BytesIO

from django.db.models import Model
from django.utils.timezone import is_aware, make_naive, now
from faker import Faker
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS, Base
from PIL.TiffImagePlugin import IFDRational

from gallery.apps import GalleryConfig
from gallery.schemas import ExifData
from personal_website.storages import StorageType, select_storage

fake = Faker(locale="ru_RU")
storage: StorageType = select_storage()


def exif_value_to_json(value: object) -> object:
    """Преобразовать значение EXIF в JSON-совместимый тип.

    Объекты PIL (IFDRational и др.) не сериализуются в JSON напрямую,
    поэтому выполняется преобразование к примитивным типам.

    Args:
        value: Исходное значение EXIF из PIL.

    Returns:
        JSON-совместимое значение (int, float, str, list) или None для пропуска.
    """
    if isinstance(value, IFDRational):
        return float(value)
    if isinstance(value, bytes):
        return None
    if isinstance(value, tuple):
        return [exif_value_to_json(v) for v in value]
    if isinstance(value, (int, float, str)):
        return value
    return str(value)


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


def compute_datetime_taken(photo: Model) -> datetime:
    """Вычислить дату и время съемки фотографии.

    Функция извлекает дату и время съемки из EXIF данных изображения.
    Если EXIF данные отсутствуют или не содержат DateTimeOriginal,
    используется время изменения файла.

    EXIF данные DateTimeOriginal не содержат информацию о часовом поясе.
    Для корректной сортировки фотографий все datetime объекты должны быть
    одного типа. Используется naive datetime (без часового пояса), поскольку
    невозможно определить часовой пояс места съемки.

    Время изменения файла, получаемое из хранилища, может быть timezone-aware
    (при USE_TZ=True). Для корректного преобразования aware datetime в naive
    используется timezone.make_naive(), который переводит время в текущий
    часовой пояс перед удалением информации о нём.

    Args:
        photo: Экземпляр модели Photo.

    Returns:
        Naive datetime (без часового пояса) с датой и временем съемки
        или текущим временем в случае отсутствия файла.
    """
    # Проверить наличие файла изображения.
    if not photo.image.name or not storage.exists(photo.image.name):
        return now()

    # Получить дату и время последнего изменения файла и преобразовать
    # timezone-aware datetime в naive с учётом текущего часового пояса.
    modified_time = storage.get_modified_time(photo.image.name)
    date_time = make_naive(modified_time) if is_aware(modified_time) else modified_time

    # Получить EXIF данные фотографии.
    photo_exif = photo.exif or {}

    # Если в EXIF отсутствует дата и время съемки,
    # то вернуть дату и время последнего изменения.
    original_exif = photo_exif.get("DateTimeOriginal")
    if not original_exif:
        return date_time

    # Получить дату и время съемки из EXIF, если не перехвачено исключение.
    # Если перехвачено исключение, то вернуть дату и время изменения файла.
    try:
        return datetime.strptime(original_exif, "%Y:%m:%d %H:%M:%S")  # noqa: DTZ007
    except ValueError:
        return date_time
