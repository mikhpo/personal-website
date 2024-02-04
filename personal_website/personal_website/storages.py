"""Определение параметров хранения загружаемых файлов."""
from django.conf import settings
from django.core.files.storage import FileSystemStorage, storages


def select_storage() -> FileSystemStorage:
    """Возвращает файловое хранилище по умолчанию."""
    return storages["test"] if settings.TEST else storages["default"]
