"""Модуль для запуска административных команд Django через CLI.

В данном модуле также указан относительный путь до модуля настроек проекта settings.py.
"""

import os
import sys
from pathlib import Path


def main() -> None:  # noqa: D103
    # Добавить родительскую директорию backend/ в PYTHONPATH
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "personal_website.settings")

    try:
        from django.core.management import execute_from_command_line  # noqa: PLC0415
    except ImportError as exc:
        msg = (
            "Не удалось импортировать Django. Вы уверены, что Django установлен "
            "и доступен по адресу, указанному в переменной окружения PYTHONPATH? "
            "Активировано ли виртуальное окружение?"
        )
        raise ImportError(
            msg,
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
