"""
Определение глобальных фикстур, используемых при запуске тестов через Pytest.
"""

import os
import shutil
from pathlib import Path

import pytest
from django.conf import settings


@pytest.fixture(scope="session", autouse=True)
def manage_temp_dir():
    """
    Создать каталог для временных файлов тестовой сессией и
    удалить временный каталог после завершения тестовой сессии.
    """
    # Получить адрес папки для временных файлов из переменных окружения.
    temp_dir = os.getenv("TEMP_ROOT")

    # Создать папку для временных файлов перед глобальным запуском тестов.
    Path(temp_dir).mkdir(parents=True, exist_ok=True)

    # Скопировать тестовые изображения в папку для тестирования.
    media_dir = settings.BASE_DIR / "media"
    shutil.copytree(media_dir, temp_dir, dirs_exist_ok=True)

    # Передать адрес временной папки как фикстуру для тестов.
    yield temp_dir

    # Удалить временную папку со всем содержимым.
    shutil.rmtree(temp_dir, ignore_errors=True)
