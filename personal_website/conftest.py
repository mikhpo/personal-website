"""Определение глобальных фикстур, используемых при запуске тестов через Pytest."""

from collections.abc import Generator
from typing import Any

import pytest
from django.conf import settings

from personal_website.utils import setup_test_environment, teardown_test_environment


@pytest.fixture(scope="session", autouse=True)
def manage_temp_dir() -> Generator[str, Any, None]:
    """Управление каталогом для временных файлов.

    Создать каталог для временных файлов тестовой сессией и
    удалить временный каталог после завершения тестовой сессии.
    """
    # Настроить тестовую среду
    setup_test_environment()

    # Передать адрес временной папки как фикстуру для тестов.
    temp_dir = settings.TEMP_ROOT
    yield str(temp_dir)

    # Очистить тестовую среду
    teardown_test_environment()
