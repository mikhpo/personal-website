"""
Скрипт для создания бэкапа базы данных PostgreSQL при помощи утилиты pg_dump.
"""

import locale
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from personal_website.utils import calculate_path_size


def remove_existing_dump(dump_path: str) -> None:
    """
    Удаление предыдущего дампа. Способ удаления зависит от типа дампа: файл или папка.
    """
    if os.path.isdir(dump_path):
        shutil.rmtree(dump_path)
    else:
        os.remove(dump_path)


def get_save_path(base_dir: str, POSTGRES_NAME: str):
    """
    Построение полного пути относительно базовой директории хранения бэкапов.
    """
    backup_dir = os.path.join(base_dir, "database", POSTGRES_NAME)
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    today = datetime.today().date()
    dump_name = f"{POSTGRES_NAME}_{today}.dump"
    dump_path = os.path.join(backup_dir, dump_name)
    return dump_path


def compose_command(
    POSTGRES_HOST: str,
    POSTGRES_PORT: str,
    POSTGRES_NAME: str,
    POSTGRES_USER: str,
    dump_path: str,
):
    """
    Составить команду pg_dump, подставив переменные окружения.
    """
    pg_dump = os.popen(f"which pg_dump").read().strip()
    dump_command = (
        f"{pg_dump} "
        + f'"host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={POSTGRES_NAME} user={POSTGRES_USER}" '
        + "--no-privileges --no-subscriptions --no-publications -Fc -f "
        + f"{dump_path}"
    )
    return dump_command


def create_dump(dump_command: str, POSTGRES_PASSWORD: str):
    """
    Запустить утилиту pg_dump для создания бэкапа базы данных.
    Возвращает кортеж из стандартного вывода и стандартной ошибки.
    """
    # Пароль от базы данных PostgreSQL передается в качестве переменной окружения.
    process = subprocess.Popen(
        args=shlex.split(dump_command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={"PGPASSWORD": POSTGRES_PASSWORD},
    )

    # Ожидаем результата выполнения bash-команды.
    stdout, stderr = process.communicate()
    return stdout, stderr


def main():
    """
    Основное тело скрипта.
    """
    try:
        print("Запущен скрипт для создания дампа базы данных PostgreSQL")

        # Получение параметров из переменных окружения.
        if load_dotenv():
            print("Переменные окружения считаны из .env файла")
        else:
            sys.exit("Не удалось считать переменные окружения из .env файла")

        POSTGRES_HOST = os.environ["POSTGRES_HOST"]
        POSTGRES_PORT = os.environ["POSTGRES_PORT"]
        POSTGRES_NAME = os.environ["POSTGRES_NAME"]
        POSTGRES_USER = os.environ["POSTGRES_USER"]
        POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

        # Определение системной кодировки.
        encoding = locale.getlocale()[1]

        # Определение пути сохранения дампа.
        base_dir = os.getenv("BACKUP_ROOT")
        dump_path = get_save_path(base_dir, POSTGRES_NAME)
        print(f"Дамп базы данных будет сохранен по адресу {dump_path}")

        # Если файл дампа сегодня уже был создан, то необходимо его удалить.
        if Path(dump_path).exists():
            print(
                f"Сегодня уже был создан дамп '{dump_path}'. "
                "Ранее созданный дамп будет удален"
            )
            remove_existing_dump(dump_path)

        # Вызовем bash скрипт для создания дампа базы данных при помощи утилиты pg_dump.
        # Аргументы для скрипта считываются из переменных окружения.
        dump_command = compose_command(
            POSTGRES_HOST, POSTGRES_PORT, POSTGRES_NAME, POSTGRES_USER, dump_path
        )
        print(f"Выполняю команду: {dump_command}")

        # Выполнить команду pg_dump.
        stdout, stderr = create_dump(dump_command, POSTGRES_PASSWORD)

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

        # Если выполнение скрипта успешно завершено, то направим в stdout
        # строку с результатом и указанием адресов получателей бэкапа.
        if Path(dump_path).exists():
            size = calculate_path_size(dump_path)
            message_size = size.get("message")
            print(
                f"Дамп базы данных PostgreSQL сохранен по адресу '{dump_path}'. "
                f"Размер дампа: {message_size}"
            )
        else:
            sys.exit("Дамп базы данных PostgreSQL не был сохранен")
    except Exception as error:
        sys.exit(f"Ошибка выполнения скрипта: {error}")


if __name__ == "__main__":
    main()
