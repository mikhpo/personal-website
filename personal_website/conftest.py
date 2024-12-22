"""Определение глобальных фикстур, используемых при запуске тестов через Pytest."""

import os
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(scope="session", autouse=True)
def manage_temp_dir() -> Generator[str, Any, None]:
    """Управление каталогом для временных файлов.

    Создать каталог для временных файлов тестовой сессией и
    удалить временный каталог после завершения тестовой сессии.
    """
    # Получить адрес папки для временных файлов из переменных окружения.
    temp_dir = os.getenv("TEMP_ROOT")

    # Создать папку для временных файлов перед глобальным запуском тестов.
    Path(temp_dir).mkdir(parents=True, exist_ok=True)

    # Передать адрес временной папки как фикстуру для тестов.
    yield str(temp_dir)

    # Удалить временную папку со всем содержимым.
    shutil.rmtree(temp_dir, ignore_errors=True)
