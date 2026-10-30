"""Коллекция вспомогательных фукнций и классов."""

import datetime
import json
import locale
import logging
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

from personal_website.storages import select_storage

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


def list_file_paths(files_dir: str) -> list[str]:
    """Определить пути набора набора файлов в указанном каталоге.

    Args:
        files_dir (str): путь до файлов.

    Returns:
        list: список полных путей до файлов.
    """
    # Получаем хранилище по умолчанию
    storage = select_storage()

    # Получаем список файлов и подкаталогов
    try:
        files, _ = storage.listdir(files_dir)
    except OSError, FileNotFoundError, ClientError:
        # Если возникла ошибка при получении списка файлов, возвращаем пустой список
        return []

    # Формируем полные пути к файлам
    paths = []
    for file_name in files:
        # Используем метод joinpath для формирования полного пути
        full_path = storage.joinpath(files_dir, file_name)
        # Проверяем, что путь ведет к файлу, а не к каталогу
        if storage.exists(full_path) and not storage.is_dir(full_path):
            paths.append(full_path)

    return paths


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


def is_s3_available() -> bool:
    """Проверить доступность S3-хранилища из настроек."""
    try:
        s3_options = settings.STORAGES["s3"]["OPTIONS"]
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=s3_options["access_key"],
            aws_secret_access_key=s3_options["secret_key"],
            endpoint_url=s3_options["endpoint_url"],
            config=Config(signature_version="s3v4"),
        )
        s3_client.list_buckets()
    except Exception:  # noqa: BLE001
        return False
    return True


def bucket_policy_document(bucket_name: str) -> str:
    """Документ bucket policy: анонимное чтение медиа и статики.

    Returns:
        str: JSON-документ политики, разрешающий s3:GetObject всем
        на префиксы медиа и статики бакета.
    """
    statements = [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/{prefix}/*",
        }
        for prefix in (settings.S3_MEDIA_LOCATION, settings.S3_STATIC_LOCATION)
    ]
    return json.dumps({"Version": "2012-10-17", "Statement": statements})


def init_s3_bucket() -> str:
    """Инициализировать новое хранилище: создать бакет и применить политику публичной раздачи.

    Правило собственности: существующий бакет не изменяется. Внешний
    провайдер (прод) всегда настроен до первого старта приложения,
    поэтому политики внешних бакетов приложению недоступны; локальный
    сервер стартует пустым и инициализируется полностью.

    Returns:
        str: "created" - бакет создан и политика применена;
        "exists" - бакет существует, изменения не выполнялись.

    Raises:
        ClientError: Сервер недоступен либо существующий бакет недоступен
            ключам (отказ доступа): такой бакет не создается и не изменяется.
    """
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
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as error:
        if error.response["Error"]["Code"] not in ("404", "NoSuchBucket"):
            raise
        s3_client.create_bucket(Bucket=bucket_name)
        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy_document(bucket_name))
        return "created"
    return "exists"


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

    # Если используется S3 в тестах, инициализировать хранилище
    if getattr(settings, "STORAGE_TYPE", "filesystem") == "s3":
        init_s3_bucket()


def teardown_test_environment() -> None:
    """Очистить тестовую среду."""
    # Очистить временную директорию
    cleanup_temp_directory()

    # Если используется S3 в тестах, очистить тестовый бакет
    if getattr(settings, "STORAGE_TYPE", "filesystem") == "s3":
        cleanup_s3_test_bucket()
