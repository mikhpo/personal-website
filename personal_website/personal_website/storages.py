"""Определение параметров хранения загружаемых файлов."""

from django.conf import settings
from django.core.files.storage import Storage, storages


def select_storage() -> Storage:
    """Возвращает файловое хранилище по умолчанию."""
    return storages["test"] if settings.TEST else storages["default"]
