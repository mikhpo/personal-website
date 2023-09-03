#!/usr/bin/env python3
#
# Скрипт для создания бэкапа базы данных PostgreSQL при помощи утилиты pg_dump.

import locale
import logging
import logging.handlers
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from distutils.util import strtobool
from pathlib import Path

from dotenv import load_dotenv


def set_logger():
    """
    Установка настроек логирования.
    """
    # Определение пути сохранения логов.
    base_dir = Path(__file__).resolve().parent.parent
    script_name = Path(__file__).resolve().stem
    logs_dir = os.path.join(base_dir, "logs", script_name)
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, f"{script_name}.log")

    # Настройки логирования.
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    formatter = logging.Formatter(
        fmt="[{asctime}] [{levelname}] [{filename} -> {funcName} -> {lineno}] {message}",
        datefmt="%d.%m.%Y %H:%M:%S",
        style="{",
    )
    timed_rotating_handler = logging.handlers.TimedRotatingFileHandler(
        log_path, when="midnight", backupCount=7
    )
    timed_rotating_handler.setFormatter(formatter)
    logger.addHandler(timed_rotating_handler)
    return logger


def get_dump_size(dump_path: str) -> str:
    """
    Определение размера дампа с автоматическим определением единцы измерения.
    """
    units = ("Б", "КБ", "МБ", "ГБ", "ТБ")

    # Определение размера дампа в байтах. Способ определения размера дампа зависит от типа дампа: файл или папка.
    if os.path.isdir(dump_path):
        size = sum([f.stat().st_size for f in Path(dump_path).glob("**/*")])
    else:
        size = os.path.getsize(dump_path)

    # Определение единцы измерения размера дампа. Значение округляется до целого числа и возвращается в виде строки с указанием размерности.
    for unit in units:
        if size < 1024:
            value = int(size)
            return f"{value} {unit}"
        size /= 1024


def remove_existing_dump(dump_path: str) -> None:
    """
    Проверяет, создан ли уже дамп.
    Если дамп создан, то удаляет предыдущий.
    Способ удаления зависит от типа дампа: файл или папка.
    """
    if Path(dump_path).exists():
        logger.info(
            f"Сегодня уже был создан дамп {dump_path}. Ранее созданный дамп будет удален"
        )
        if os.path.isdir(dump_path):
            shutil.rmtree(dump_path)
        else:
            os.remove(dump_path)


def get_save_path(base_dir: str, pg_name: str):
    """
    Построение полного пути относительно базовой директории хранения бэкапов.
    """
    backup_dir = os.path.join(base_dir, "database", pg_name)
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    today = datetime.today().date()
    dump_name = f"{pg_name}_{today}.dump"
    dump_path = os.path.join(backup_dir, dump_name)
    return dump_path


def compose_command(
    pg_host: str, pg_port: str, pg_name: str, pg_user: str, dump_path: str
):
    """
    Составить команду pg_dump, подставив переменные окружения.
    """
    pg_dump = os.popen(f"which pg_dump").read().strip()
    dump_command = (
        f"{pg_dump} "
        f'"host={pg_host} port={pg_port} dbname={pg_name} user={pg_user}" '
        "--no-privileges --no-subscriptions --no-publications -Fc -f "
        f"{dump_path}"
    )
    return dump_command


def create_dump(dump_command: str, pg_password: str):
    """
    Запустить утилиту pg_dump для создания бэкапа базы данных.
    Возвращает кортеж из стандартного вывода и стандартной ошибки.
    """
    # Пароль от базы данных PostgreSQL передается в качестве переменной окружения.
    process = subprocess.Popen(
        args=shlex.split(dump_command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={"PGPASSWORD": pg_password},
    )

    # Ожидаем результата выполнения bash-команды.
    stdout, stderr = process.communicate()
    return stdout, stderr


def main():
    """
    Основное тело скрипта.
    """
    logger.info("Запущен скрипт для создания дампа базы данных PostgreSQL")

    # Получение параметров из переменных окружения.
    logger.info(
        "Считывание переменных окружения из файла .env в корневой директории проекта"
    )
    load_dotenv()
    pg_host = os.environ["PG_HOST"]
    pg_port = os.environ["PG_PORT"]
    pg_name = os.environ["PG_NAME"]
    pg_user = os.environ["PG_USER"]
    pg_password = os.environ["PG_PASSWORD"]
    debug = bool(strtobool(os.environ["DEBUG"]))

    # Определение системной кодировки.
    encoding = locale.getlocale()[1]

    # Определение пути сохранения дампа.
    base_dir = os.getenv("BACKUP_ROOT")
    dump_path = get_save_path(base_dir, pg_name)
    logger.info(f"Дамп базы данных будет сохранен по адресу {dump_path}")

    # Если файл дампа сегодня уже был создан, то необходимо его удалить.
    remove_existing_dump(dump_path)

    # Вызовем bash скрипт для создания дампа базы данных при помощи утилиты pg_dump. Аргументы для скрипта считываются из переменных окружения.
    dump_command = compose_command(pg_host, pg_port, pg_name, pg_user, dump_path)
    logger.info(f"Выполняю команду: {dump_command}")

    # Выполнить команду pg_dump.
    stdout, stderr = create_dump(dump_command, pg_password)

    # Стандартный вывод и стандартная ошибка являются байтами,
    # которые необходимо преобразовать в строку для лучшего форматирования.
    if stderr:
        sys.exit(stderr.decode(encoding=encoding))
    elif len(stdout) > 0:
        logger.info(stdout.decode(encoding=encoding))
    else:
        logger.info("Выполнение команды завершено")

    # Если выполнение скрипта успешно завершено, то направим в stdout
    # строку с результатом и указанием адресов получателей бэкапа.
    if Path(dump_path).exists():
        size = get_dump_size(dump_path)
        logger.info(
            f"Дамп базы данных PostgreSQL сохранен по адресу {dump_path}. Размер дампа: {size}"
        )
    else:
        sys.exit("Дамп базы данных PostgreSQL не был сохранен")


if __name__ == "__main__":
    logger = set_logger()
    try:
        main()
    except BaseException as e:
        logger.exception(e)
