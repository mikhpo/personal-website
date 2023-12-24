#!/usr/bin/env python3
#
# Скрипт для восстановления базы данных PostgreSQL из дампа.

import argparse
import locale
import os
import shlex
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

from personal_website.utils import calculate_path_size


def parse_argument() -> str:
    """
    Парсер адреса дампа из аргументов командной строки.
    """
    parser = argparse.ArgumentParser(
        description="Восстановление базы данных PostgreSQL из дампа",
        epilog="Внимание! Выполнение данного скрипта может привести к потере данных!",
    )
    parser.add_argument("dump_path", type=str, nargs="?", help="Полный адрес дампа")
    dump_path = parser.parse_args().dump_path
    if not dump_path:
        dump_path = input(
            "Не указан адрес дампа. Пожалуйста, укажите полный адрес дампа: "
        )
    return dump_path


def verify_command():
    """
    Предлагает пользователю убедиться в намерениях выполнить скрипт.
    """
    answer = input(
        "Внимание! Выполнение данного скрипта может привести к потере данных!\n"
        "Вы уверены, что желаете продолжить выполнение скрипта? [y/n] "
    )
    if answer.lower() == "n":
        sys.exit("Выполнение скрипта было отменено")


def check_dump(dump_path: str):
    """
    Проверяет, указан ли путь к дампу в аргументах скрипта и, если указан, то корректный ли.
    """
    if not dump_path:
        sys.exit("Вы не указали адрес дампа!")
    else:
        if not Path(dump_path).exists():
            sys.exit("Указанный путь не существует")
    return dump_path


def main() -> None:
    # Получить адрес дампа.
    dump_path = parse_argument()
    print(f"Запущен скрипт для восстановления базы данных из дампа '{dump_path}'")
    verify_command()
    dump_path = check_dump(dump_path)

    # Определить размер дампа.
    dump_size = calculate_path_size(dump_path)
    verbose_size = dump_size.get("message")
    print(f"Размер дампа составляет {verbose_size}")

    # Загрузка переменных окружения из файла .env в корневой директории проекта.
    if load_dotenv():
        print("Переменные окружения считаны из .env файла")
    else:
        sys.exit("Не удалось считать переменные окружения из .env файла")

    POSTGRES_HOST = os.environ["POSTGRES_HOST"]
    POSTGRES_USER = os.environ["POSTGRES_USER"]
    POSTGRES_PORT = os.environ["POSTGRES_PORT"]
    POSTGRES_NAME = os.environ["POSTGRES_NAME"]
    POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

    # Определение системной кодировки.
    encoding = locale.getlocale()[1]

    # Вызовем bash скрипт для восстановления базы данных из дампа при помощи утилиты pg_restore.
    # Аргументы для скрипта считываются из модуля settings.
    pg_restore = os.popen(f"which pg_restore").read().strip()
    bash_script = (
        f"{pg_restore} -Fc --single-transaction --no-owner --clean "
        + f"-h {POSTGRES_HOST} -U {POSTGRES_USER} -p {POSTGRES_PORT} -d {POSTGRES_NAME} "
        + f"{dump_path}"
    )
    print(f"Выполняю команду: {bash_script}")

    # Синхронный вызов bash-скрипта.
    process = subprocess.Popen(
        args=shlex.split(bash_script),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={"PGPASSWORD": POSTGRES_PASSWORD},
    )

    # Ожидаем результата выполнения bash-команды.
    stdout, stderr = process.communicate()

    # Стандартный вывод и стандартная ошибка являются байтами,
    # которые необходимо преобразовать в строку для лучшего форматирования.
    if stderr:
        message = stderr.decode(encoding=encoding)
        sys.exit(message)
    elif len(stdout) > 0:
        message = stdout.decode(encoding=encoding)
        print(message)
    else:
        print("Выполнение команды завершено")

    # Если выполнение скрипта успешно завершено, то направим в stdout сообщение о результате.
    print("База данных PostgreSQL восстановлена из дампа")


if __name__ == "__main__":
    main()
