"""Определение глобальных фикстур, используемых при запуске тестов через Pytest."""

import re
from collections.abc import Generator
from typing import Any

import pytest
from django.conf import settings
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.signals import connection_created
from django.dispatch import receiver

from personal_website.utils import setup_test_environment, teardown_test_environment


def _sqlite_unicode_like(*args: object) -> int:
    """Аналог функции LIKE SQLite с юникод-регистронезависимостью.

    Штатный LIKE SQLite сворачивает регистр только для ASCII, поэтому
    icontains-поиск по кириллице в тестах на SQLite (SOURCECRAFT_CI) не
    находит совпадений, отличающихся регистром. Аргументы совпадают
    со встроенной функцией: шаблон, строка, опциональный символ экранирования.
    """
    match args:
        case (pattern, value):
            escape = None
        case (pattern, value, escape):
            pass
        case _:
            return 0
    if pattern is None or value is None:
        return 0
    pattern_str = str(pattern)
    value_str = str(value)
    parts: list[str] = ["^"]
    index = 0
    while index < len(pattern_str):
        char = pattern_str[index]
        if escape is not None and char == escape and index + 1 < len(pattern_str):
            index += 1
            parts.append(re.escape(pattern_str[index]))
        elif char == "%":
            parts.append(".*")
        elif char == "_":
            parts.append(".")
        else:
            parts.append(re.escape(char))
        index += 1
    parts.append("$")
    return 1 if re.match("".join(parts), value_str, re.IGNORECASE) else 0


@receiver(connection_created)
def register_unicode_like(sender: object, connection: BaseDatabaseWrapper, **kwargs: object) -> None:  # noqa: ARG001
    """Заменить функцию LIKE SQLite на юникод-регистронезависимую."""
    if connection.vendor == "sqlite":
        connection.connection.create_function("LIKE", -1, _sqlite_unicode_like)


@pytest.fixture(scope="session", autouse=True)
def manage_temp_dir() -> Generator[str, Any, None]:
    """Управление каталогом для временных файлов.

    Создать каталог для временных файлов тестовой сессией и
    удалить временный каталог после завершения тестовой сессии.
    """
    # Настроить тестовую среду
    setup_test_environment()

    # Передать адрес временного каталога как фикстуру для тестов.
    temp_dir = settings.TEMP_ROOT
    yield str(temp_dir)

    # Очистить тестовую среду
    teardown_test_environment()
