"""Коллекция вспомогательных фукнций и классов."""

import datetime
import locale
import logging
import os
import re
import shutil
from pathlib import Path

import boto3  # type: ignore[import-untyped]
from botocore.client import Config  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from django.conf import settings
from django.db.models import Model
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker
from pytils import translit  # type: ignore[import-untyped]

fake = Faker(locale="ru_RU")


def str_to_bool(val: str) -> bool:
    """Адаптированная имплементация функции strtobool из стандартной библиотеки distutils."""
    if not val:
        return False
    value = val.lower()
    if value in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif value in ("n", "no", "f", "false", "off", "0"):  # noqa: RET505
        return False
    else:
        msg = f"Неверное значение аргумента {val}"
        raise ValueError(msg)


def is_running_in_container() -> bool:
    """Проверяет, запущено ли приложение внутри контейнера и возвращает логическое значение."""
    return bool(Path("/proc/1/cgroup").exists())


def format_local_datetime(date_time: datetime.datetime) -> str:
    """Преобразует дату-время в строку с учетом локализации и временной зоны."""
    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
    if timezone.is_aware(date_time):
        date_time = timezone.localtime(date_time)
    return f"{date_time.day} {date_time:%B} {date_time.year} г. {date_time.hour}:{date_time:%M}"


class NoColorLogFormatter(logging.Formatter):
    """Бесцветное форматирование для вывода логов в файлы.

    Обесцвечивание достигается путем удаления символов соответствующей ANSI-кодировки.
    Дополнительно создается атрибут текущего времени в формате "01.01.2001".
    """

    # Регулярное выражение, соответствующее символам ANSI-кодировки.
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")

    def format(self, record: logging.LogRecord) -> str:  # noqa: D102
        if self.uses_asctime() and not hasattr(record, "asctime"):
            record.asctime = self.formatTime(record, "%d.%m.%Y %H:%M:%S")
        record.msg = re.sub(self.ansi_re, "", record.msg)
        return super().format(record)

    def uses_asctime(self) -> bool:  # noqa: D102
        return self._fmt.find("{asctime}") >= 0  # type: ignore[union-attr]


def list_file_paths(files_dir: Path) -> list[str]:
    """Определить пути набора набора файлов в указанном каталоге.

    Args:
        files_dir (str): путь до файлов.

    Returns:
        list: список полных путей до файлов.
    """
    names = os.listdir(files_dir)
    paths = [Path(files_dir).joinpath(name) for name in names]
    return [str(path) for path in paths if Path(path).is_file()]


def calculate_path_size(path: str) -> dict | None:
    """Определение размера файла или каталога по указанному пути с автоматическим определением единцы измерения.

    Args:
        path (str): путь до файла или каталога.

    Returns:
        dict: словарь, содержащий значение, единицу измерения и сообщение.

    Examples:
        ```
        {"value": 500, "unit": "КБ", "message": "500 КБ"}
        ```
    """
    units = ("Б", "КБ", "МБ", "ГБ", "ТБ")
    binary_thousand = 1024
    size: float | int = 0

    # Способ определения размера дампа зависит от типа пути: файл или каталог.
    if Path(path).is_dir():
        for _path, _, files in os.walk(path):
            for file in files:
                filepath = Path(_path) / file
                size += Path(filepath).stat().st_size
    else:
        size = Path(path).stat().st_size

    # Определение единцы измерения размера дампа. Значение округляется до целого числа.
    for unit in units:
        if size < binary_thousand:
            value = int(size)
            return {"value": value, "unit": unit, "message": f"{value} {unit}"}
        size /= binary_thousand
    return None


def has_cyrillic(text: str) -> bool:
    """Проверяет наличие в тексте кириллических символов."""
    return bool(re.search("[а-яА-Я]", text))


def get_slug(text: str) -> str:
    """Создает слаг из текста."""
    if has_cyrillic(text):
        return translit.slugify(text)
    return slugify(text)


def get_unique_slug(instance: Model, text: str, max_length: int = 50) -> str:
    """Создает уникальный слаг, уникальный для данного класса."""
    model = instance.__class__
    truncated_text = text if len(text) <= max_length else text[:max_length]
    slug = get_slug(truncated_text)
    n = 1
    while model.objects.filter(slug=slug).exists():
        n += 1
        slug = f"{slug}-{n}"
    return slug


def generate_random_text(word_count: int) -> str:
    """Генерирует случайный текст, состоящий из заданного количества слов.

    Args:
        word_count (int): количество слов в тексте.
    """
    random_words = fake.words(word_count)
    return " ".join(random_words)


def cleanup_temp_directory() -> None:
    """Очистить временную директорию."""
    shutil.rmtree(settings.TEMP_ROOT, ignore_errors=True)


def create_s3_test_bucket() -> None:
    """Создать тестовый бакет S3, если он не существует."""
    # Получить настройки S3 из конфигурации хранилища
    s3_options = settings.STORAGES["s3"]["OPTIONS"]

    # Создать клиент S3
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=s3_options["access_key"],
        aws_secret_access_key=s3_options["secret_key"],
        region_name=s3_options["region_name"],
        endpoint_url=s3_options["endpoint_url"],
        config=Config(signature_version="s3v4"),
    )

    bucket_name = s3_options["bucket_name"]
    # Пытаемся создать бакет
    try:
        s3_client.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        # Если бакет уже существует и принадлежит нам, это не ошибка
        if e.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
            # Для всех других ошибок пробрасываем исключение дальше
            raise


def cleanup_s3_test_bucket() -> None:
    """Очистить тестовый бакет S3 от временных файлов."""
    # Получить настройки S3 из конфигурации хранилища
    s3_options = settings.STORAGES["s3"]["OPTIONS"]

    # Создать клиент S3
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=s3_options["access_key"],
        aws_secret_access_key=s3_options["secret_key"],
        region_name=s3_options["region_name"],
        endpoint_url=s3_options["endpoint_url"],
    )

    bucket_name = s3_options["bucket_name"]

    # Получить список всех объектов в бакете
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name)

    # Удалить все объекты
    delete_keys = []
    for page in pages:
        if "Contents" in page:
            delete_keys.extend({"Key": obj["Key"]} for obj in page["Contents"])

    # Выполнить массовое удаление
    if delete_keys:
        s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={"Objects": delete_keys},
        )


def setup_test_environment() -> None:
    """Настроить тестовую среду."""
    # Создать папку для временных файлов
    Path(settings.TEMP_ROOT).mkdir(parents=True, exist_ok=True)

    # Скопировать тестовые изображения, если директория media существует
    media_dir = settings.BASE_DIR / "media"
    if Path(media_dir).exists():
        shutil.copytree(media_dir, settings.TEMP_ROOT, dirs_exist_ok=True)

    # Если используется S3 в тестах, создать тестовый бакет
    if getattr(settings, "STORAGE_TYPE", "filesystem") == "s3":
        create_s3_test_bucket()


def teardown_test_environment() -> None:
    """Очистить тестовую среду."""
    # Очистить временную директорию
    cleanup_temp_directory()

    # Если используется S3 в тестах, очистить тестовый бакет
    if getattr(settings, "STORAGE_TYPE", "filesystem") == "s3":
        cleanup_s3_test_bucket()
