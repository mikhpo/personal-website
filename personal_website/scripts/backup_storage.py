"""
Скрипт для создания бэкапа хранилища персонального сайта: медиа и загруженных файлов.
"""

import locale
import os
import shlex
import subprocess
import sys

from dotenv import load_dotenv

from personal_website.utils import calculate_path_size


def get_source_path():
    """
    Получить адрес папки-источника.
    """
    source_dir = os.getenv("STORAGE_ROOT")
    source_dir += os.sep
    return source_dir


def get_destination_path():
    """
    Получить адрес папки-назначения.
    """
    backup_dir = os.getenv("BACKUP_ROOT")
    destination_dir = os.path.join(backup_dir, "storage")
    destination_dir += os.sep
    return destination_dir


def compose_command(source_path: str, destination_path: str):
    """
    Составить текст команды rsync.
    """
    rsync = os.popen(f"which rsync").read().strip()
    rsync_command = f"{rsync} -r {source_path} {destination_path}"
    return rsync_command


def run_rsync(rsync_command: str):
    """
    Выполннить команду rsync для синхронизации содержимого каталогов.
    Получить стандартный вывод или стандартную ошибку.
    """
    process = subprocess.Popen(
        args=shlex.split(rsync_command), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Ожидаем результата выполнения bash-команды.
    stdout, stderr = process.communicate()
    return stdout, stderr


def main():
    """
    Основное тело скрипта.
    """
    try:
        print("Запущен скрипт для создания бэкапа загруженных файлов проекта")

        # Получение параметров из переменных окружения.
        if load_dotenv():
            print("Переменные окружения считаны из .env файла")
        else:
            sys.exit("Не удалось считать переменные окружения из .env файла")

        # Определение системной кодировки.
        encoding = locale.getlocale()[1]

        # Определение путей копирования файлов.
        source_path = get_source_path()
        destination_path = get_destination_path()
        print(f"Адрес папки-источника: {source_path}")
        print(f"Адрес папки-назначения: {destination_path}")

        # Определение размера копируемых файлов.
        storage_size = calculate_path_size(source_path)
        message_size = storage_size.get("message")
        print(f"Общий размер хранилища: {message_size}")

        # Выполнить команду rsync, подставив переменные, и получить ответ.
        rsync_command = compose_command(source_path, destination_path)
        print(f"Выполнение команды: {rsync_command}")
        stdout, stderr = run_rsync(rsync_command)

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
    except Exception as error:
        sys.exit(f"Ошибка выполнения скрипта: {error}")


if __name__ == "__main__":
    main()
