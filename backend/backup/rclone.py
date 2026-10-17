"""Операции копирования инструментом rclone.

Функции выполняют операции над адресами целей (локальный путь или
remote:путь): выгрузка дампов, листинг, ретеншн, подсчет объектов,
синхронизация медиа. Адресация медиа-хранилища - backup.utils,
запуск субпроцессов - backup.process. Новый инструмент бэкапирования
пишется параллельным модулем с теми же именами функций.
"""

import json
import subprocess

from django.core.management.base import CommandError

from backup.process import run_command
from backup.utils import media_rclone_address, media_rclone_env

FRESHNESS_WINDOW = "25h"  # окно свежести дампа в синтаксисе длительностей rclone


def count_lines(result: subprocess.CompletedProcess[str]) -> int:
    r"""Число непустых строк захваченного вывода.

    Args:
        result (subprocess.CompletedProcess[str]): Результат команды
            со списком объектов (rclone lsf).

    Returns:
        int: Количество непустых строк stdout; для вывода
        "img1.jpg\\nimg2.jpg\\n" вернет 2.

    Example:
        >>> result = run_command(["printf", "a\\nb\\n\\n"], capture=True)
        >>> count_lines(result)
        2
    """
    return len([line for line in (result.stdout or "").splitlines() if line.strip()])


def push_dump(address: str, dump_path: str, dump_name: str) -> None:
    """Скопировать файл дампа в db/ цели.

    Args:
        address (str): Адрес хранилища цели.
        dump_path (str): Локальный путь к файлу дампа.
        dump_name (str): Имя файла дампа в db/ цели.

    Raises:
        CommandError: Копирование завершилось с ошибкой.
    """
    run_command(["rclone", "copyto", dump_path, f"{address}/db/{dump_name}"])


def dumps(address: str) -> list[str]:
    """Перечислить имена дампов в db/ цели.

    Args:
        address (str): Адрес хранилища цели.

    Returns:
        list[str]: Имена файлов дампов.

    Raises:
        CommandError: Листинг завершился с ошибкой (например, db/ недоступен).
    """
    result = run_command(["rclone", "lsf", "--files-only", f"{address}/db"], capture=True)
    return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]


def dump_source_command(address: str, dump_name: str) -> list[str]:
    """Команда, выводящая дамп из db/ цели в stdout.

    Args:
        address (str): Адрес хранилища цели.
        dump_name (str): Имя файла дампа.

    Returns:
        list[str]: Аргументы команды для pipe_commands или run_command.

    Example:
        >>> dump_source_command("/mnt/backup", "db_2026.dump")
        ['rclone', 'cat', '/mnt/backup/db/db_2026.dump']
    """
    return ["rclone", "cat", f"{address}/db/{dump_name}"]


def prune_dumps(address: str, retention_days: int) -> None:
    """Удалить дампы старше retention_days дней из db/ цели.

    Args:
        address (str): Адрес хранилища цели.
        retention_days (int): Срок хранения дампов в днях.

    Raises:
        CommandError: Удаление завершилось с ошибкой.
    """
    run_command(
        ["rclone", "delete", f"{address}/db", "--min-age", f"{retention_days}d", "--include", "*.dump"],
    )


def has_fresh_dump(address: str) -> bool:
    """Признак наличия в db/ цели дампа моложе окна свежести.

    Args:
        address (str): Адрес хранилища цели.

    Returns:
        bool: True, если за окно FRESHNESS_WINDOW появлялся *.dump.
    """
    result = run_command(
        ["rclone", "lsf", "--files-only", "--max-age", FRESHNESS_WINDOW, "--include", "*.dump", f"{address}/db"],
        capture=True,
    )
    return bool((result.stdout or "").strip())


def media_count(address: str) -> int:
    """Число объектов в storage/ цели (0 при отсутствии storage/).

    Args:
        address (str): Адрес хранилища цели.

    Returns:
        int: Количество объектов; 0 также при недоступном storage/.
    """
    result = run_command(
        ["rclone", "lsf", "--recursive", "--files-only", f"{address}/storage"],
        capture=True,
        check=False,
    )
    return count_lines(result)


def sync_media(address: str) -> None:
    """Зеркально синхронизировать медиа-хранилище в storage/ цели.

    Зеркало удаляет из цели объекты, исчезнувшие из хранилища.
    При STORAGE_TYPE=s3 медиа-бакет открывается через remote media,
    собираемый из RCLONE_CONFIG_* (см. backup.utils.media_rclone_env).

    Args:
        address (str): Адрес хранилища цели.

    Raises:
        CommandError: Синхронизация завершилась с ошибкой.
    """
    run_command(["rclone", "sync", media_rclone_address(), f"{address}/storage"], env=media_rclone_env())


def pull_media(address: str) -> None:
    """Скопировать storage/ цели в медиа-хранилище без удаления лишних файлов.

    Args:
        address (str): Адрес хранилища цели.

    Raises:
        CommandError: Копирование завершилось с ошибкой.
    """
    run_command(["rclone", "copy", f"{address}/storage", media_rclone_address()], env=media_rclone_env())


def media_size() -> tuple[int, int]:
    """Число и суммарный объем объектов медиа-хранилища через rclone size.

    Returns:
        tuple[int, int]: Количество объектов и суммарный размер в байтах.

    Raises:
        CommandError: Вывод rclone поврежден.
    """
    result = run_command(
        ["rclone", "size", "--json", media_rclone_address()],
        env=media_rclone_env(),
        capture=True,
    )
    try:
        stats = json.loads(result.stdout)
    except ValueError as error:
        msg = f"некорректный вывод rclone size: {result.stdout!r}"
        raise CommandError(msg) from error
    return int(stats.get("count", 0)), int(stats.get("bytes", 0))
