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


def verify_command():
    """
    Предлагает пользователю убедиться в намерениях выполнить скрипт.
    """
    answer = input(
        "Внимание! Выполнение данного скрипта может привести к потере данных!\n"
        "Вы уверены, что желаете продолжить выполнение скрипта? [y/n]"
    )
    if answer.lower() == "n":
        sys.exit("Выполнение скрипта было отменено")


def check_dump(dump_path: str):
    """
    Проверяет, указан ли путь к дампу в аргументах скрипта и, если указан, то корректный ли.
    """
    if not dump_path:
        dump_path = input(
            "Не указан адрес дампа. Пожалуйста, укажите полный адрес дампа: "
        )
        if not dump_path:
            sys.exit("Вы не указали адрес дампа!")
        else:
            if not Path(dump_path).exists():
                sys.exit("Указанный путь не существует")
    return dump_path


def main(dump_path: str) -> None:
    print(f"Запущен скрипт для восстановления базы данных из дампа {dump_path}")

    # Загрузка переменных окружения из файла .env в корневой директории проекта.
    print("Загрузка переменных окружения из файла .env")
    load_dotenv()
    pg_host = os.environ["PG_HOST"]
    pg_user = os.environ["PG_USER"]
    pg_port = os.environ["PG_PORT"]
    pg_name = os.environ["PG_NAME"]
    pg_password = os.environ["PG_PASSWORD"]

    # Определение системной кодировки.
    encoding = locale.getlocale()[1]

    # Вызовем bash скрипт для восстановления базы данных из дампа при помощи утилиты pg_restore.
    # Аргументы для скрипта считываются из модуля settings.
    pg_restore = os.popen(f"which pg_restore").read().strip()
    bash_script = (
        f"{pg_restore} -Fc --single-transaction --no-owner "
        f"-h {pg_host} -U {pg_user} -p {pg_port} -d {pg_name} "
        f"{dump_path}"
    )
    print(f"Выполняю команду: {bash_script}")

    # Синхронный вызов bash-скрипта.
    process = subprocess.Popen(
        args=shlex.split(bash_script),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={"PGPASSWORD": pg_password},
    )

    # Ожидаем результата выполнения bash-команды.
    stdout, stderr = process.communicate()

    # Стандартный вывод и стандартная ошибка являются байтами,
    # которые необходимо преобразовать в строку для лучшего форматирования.
    if stderr:
        sys.exit(stderr.decode(encoding=encoding))
    elif len(stdout) > 0:
        print(stdout.decode(encoding=encoding))
    else:
        print("Выполнение команды завершено")

    # Если выполнение скрипта успешно завершено, то направим в stdout сообщение о результате.
    print("База данных PostgreSQL восстановлена из дампа")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Восстановление базы данных PostgreSQL из дампа"
    )
    parser.add_argument("dump_path", type=str, nargs="?", help="Полный адрес дампа")
    dump_path = parser.parse_args().dump_path
    verify_command()
    dump_path = check_dump(dump_path)
    main(dump_path)
