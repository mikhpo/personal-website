"""Оркестрация системы резервного копирования.

Выполнение операций над БД и медиа: создание дампов, зеркальная
синхронизация в цели, проверка целей (verify), восстановление
и локальный ретеншн. Операции копирования - функции с адресом цели
(rclone) параметром, адресация медиа-хранилища - backup.utils,
запуск внешних команд - backup.process.
"""

import json
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import CommandError

from backup.process import pipe_commands, run_command
from backup.utils import (
    BYTES_PER_KIB,
    DUMP_FLAGS,
    RETENTION_SLACK_DAYS,
    SECONDS_PER_DAY,
    BackupTarget,
    dump_filename,
    is_s3,
    latest_dump,
    load_target_list,
    media_rclone_address,
    media_rclone_env,
    pg_env,
    require_media_env,
    require_pg_env,
    resolve_target,
)

logger = logging.getLogger(__name__)

FRESHNESS_WINDOW = "25h"


# --- Цели: операции копирования ----------------------------------------------


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


# --- БД: бэкап ---------------------------------------------------------------


def dump_database() -> tuple[str, str]:
    """Создать дамп БД и проверить его читаемость; вернуть имя и путь.

    Дамп пишется утилитой pg_dump в BACKUP_ROOT/db/ и проверяется чтением
    оглавления pg_restore -l.

    Returns:
        tuple[str, str]: Имя файла дампа и путь к нему.

    Raises:
        CommandError: Не заданы параметры БД, pg_dump/pg_restore не найдены,
            дамп не создан, пуст или не читается.

    Example:
        >>> dump_name, dump_path = dump_database()
        >>> dump_name.endswith(".dump")
        True
    """
    require_pg_env()
    db_name = settings.DATABASES["default"]["NAME"]
    dump_name = dump_filename(db_name)
    dump_dir = Path(settings.BACKUP_ROOT) / "db"
    dump_dir.mkdir(parents=True, exist_ok=True)
    dump_path = dump_dir / dump_name
    logger.info("Создание дампа БД %s: %s", db_name, dump_path)
    if not shutil.which("pg_dump"):
        msg = "локальный pg_dump не найден: установите клиент PostgreSQL или запустите приложение в Docker Compose"
        raise CommandError(msg)
    run_command(["pg_dump", *DUMP_FLAGS, "-f", str(dump_path)], env=pg_env())
    if not dump_path.is_file() or dump_path.stat().st_size == 0:
        msg = f"дамп не создан или пуст: {dump_path}"
        raise CommandError(msg)
    result = run_command(
        ["pg_restore", "-l", str(dump_path)],
        env=pg_env(),
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        msg = f"созданный дамп не читается pg_restore -l: {dump_path}"
        raise CommandError(msg)
    size_kb = dump_path.stat().st_size // BYTES_PER_KIB
    logger.info("Дамп создан: %s (%s KiB)", dump_path, size_kb)
    return dump_name, str(dump_path)


def apply_local_retention(backup_root: str, retention_days: int) -> None:
    """Удалить локальные дампы старше порога (аналог find -mtime +N).

    Args:
        backup_root (str): Каталог резервных копий (BACKUP_ROOT); дампы
            ищутся в его подкаталоге db/.
        retention_days (int): Срок хранения дампов в днях.
    """
    cutoff = time.time() - (retention_days - RETENTION_SLACK_DAYS) * SECONDS_PER_DAY
    db_dir = Path(backup_root) / "db"
    if not db_dir.is_dir():
        return
    for entry in db_dir.iterdir():
        if entry.is_file() and entry.name.endswith(".dump") and entry.stat().st_mtime < cutoff:
            entry.unlink()


def apply_retention(db_targets: list[BackupTarget], retention_days: int) -> None:
    """Удалить дампы старше retention_days дней в целях и локально.

    Args:
        db_targets (list[BackupTarget]): Разрешенные цели БД.
        retention_days (int): Срок хранения дампов в днях.
    """
    logger.info("Ретеншн дампов: %s дней", retention_days)
    for target in db_targets:
        prune_dumps(target.address, retention_days)
    apply_local_retention(settings.BACKUP_ROOT, retention_days)


def verify_db_targets(db_targets: list[str]) -> None:
    """Проверка целей БД: свежесть дампов и читаемость последнего.

    Дамп не выгружается на диск: оглавление читается конвейером
    dump_source_command | pg_restore -l.

    Args:
        db_targets (list[str]): Имена целей БД.

    Raises:
        CommandError: Хотя бы одна цель недоступна, без дампов, с нечитаемым
            или несвежим дампом.
    """
    failures = 0
    for name in db_targets:
        target = resolve_target(name)
        try:
            target_dumps = dumps(target.address)
        except CommandError:
            logger.info("Цель %s (БД): недоступна", name)
            failures += 1
            continue
        if not target_dumps:
            logger.info("Цель %s (БД): дампов нет", name)
            failures += 1
            continue
        latest = latest_dump(target_dumps)
        fresh = has_fresh_dump(target.address)
        try:
            pipe_commands(dump_source_command(target.address, latest), ["pg_restore", "-l"], env=pg_env())
        except CommandError:
            logger.info("Цель %s (БД): дамп %s не читается pg_restore -l", name, latest)
            failures += 1
        else:
            logger.info(
                "Цель %s (БД): дамп %s, свежесть %s, pg_restore -l ок",
                name,
                latest,
                "да" if fresh else "нет",
            )
        if not fresh:
            failures += 1
    if failures:
        msg = f"проверка целей БД завершилась с ошибками: {failures}"
        raise CommandError(msg)
    logger.info("Проверка целей БД пройдена")


def backup_db(*, verify: bool = False) -> dict[str, Any] | None:
    """Резервное копирование БД в цели либо проверка целей (verify=True).

    Список целей берется из BACKUP_DB_TARGETS; при пустом списке бэкап
    пропускается с записью в журнал, а проверка считается ошибкой.
    После копирования выполняется ретеншн BACKUP_DB_RETENTION_DAYS.

    Args:
        verify (bool): True - проверить существующие дампы целей вместо
            создания нового дампа.

    Returns:
        dict[str, Any] | None: Данные для отчета (цели, имя и объем дампа,
        ретеншн, число оставшихся дампов) при реальном запуске; None при
        проверке целей либо пустом списке целей.

    Raises:
        CommandError: При verify=True цели не настроены либо проверка
            выявила ошибки; при бэкапе - отказ дампа или копирования.

    Example:
        >>> backup_db()  # эквивалент: python backend/manage.py backup_db
        >>> backup_db(verify=True)  # эквивалент: backup_db --verify
    """
    db_targets = load_target_list(settings.BACKUP_DB_TARGETS)
    if verify:
        if not db_targets:
            msg = "цели БД не настроены: BACKUP_DB_TARGETS пуст"
            raise CommandError(msg)
        verify_db_targets(db_targets)
        return None
    if not db_targets:
        logger.info("БД не копируется: BACKUP_DB_TARGETS пуст")
        return None
    resolved = [resolve_target(name) for name in db_targets]
    dump_name, dump_path = dump_database()
    dump_size = Path(dump_path).stat().st_size
    for target in resolved:
        logger.info("Копирование дампа в цель %s", target.describe())
        push_dump(target.address, dump_path, dump_name)
    apply_retention(resolved, settings.BACKUP_DB_RETENTION_DAYS)
    remaining = len(list((Path(settings.BACKUP_ROOT) / "db").glob("*.dump")))
    logger.info("Резервное копирование БД завершено")
    return {
        "targets": [target.describe() for target in resolved],
        "dump_name": dump_name,
        "dump_size": dump_size,
        "retention_days": settings.BACKUP_DB_RETENTION_DAYS,
        "remaining": remaining,
    }


# --- БД: восстановление ------------------------------------------------------


def pg_restore_args() -> list[str]:
    """Аргументы pg_restore для полного восстановления текущей БД.

    Returns:
        list[str]: Команда с флагами формата, очистки объектов перед
        восстановлением (--clean --if-exists) и именем базы из настроек;
        путь к файлу дампа или чтение из stdin добавляет вызывающий.

    Example:
        >>> pg_restore_args()
        ['pg_restore', '-Fc', '--no-owner', '--no-privileges', '--clean', '--if-exists', '-d', 'personal_website']
    """
    db_name = settings.DATABASES["default"]["NAME"]
    return ["pg_restore", "-Fc", "--no-owner", "--no-privileges", "--clean", "--if-exists", "-d", db_name]


def ensure_pg_restore() -> None:
    """Проверить параметры БД и наличие локального pg_restore.

    Raises:
        CommandError: Не заданы параметры БД либо pg_restore не найден.
    """
    require_pg_env()
    if not shutil.which("pg_restore"):
        msg = "локальный pg_restore не найден: установите клиент PostgreSQL или запустите приложение в Docker Compose"
        raise CommandError(msg)


def restore_database(dump_path: str) -> None:
    """Восстановить БД из дампа по пути на диске.

    Args:
        dump_path (str): Путь к файлу дампа в формате pg_dump -Fc.

    Raises:
        CommandError: Параметры БД не заданы, pg_restore не найден либо
            восстановление завершилось с ошибкой.

    Example:
        >>> restore_database("/srv/backups/db/personal_website_2026-08-25_1301.dump")
    """
    ensure_pg_restore()
    logger.info("Восстановление БД из %s", dump_path)
    run_command([*pg_restore_args(), dump_path], env=pg_env())
    logger.info("База данных восстановлена")


def restore_dump_stream(source_command: list[str]) -> None:
    """Восстановить БД из потока дампа, передаваемого источником в stdout.

    Дамп не выгружается на диск: источник (rclone cat) передается
    в pg_restore конвейером через канал в памяти.

    Args:
        source_command (list[str]): Команда источника, выводящая дамп
            в stdout (см. dump_source_command).

    Raises:
        CommandError: Параметры БД не заданы, pg_restore не найден либо
            конвейер завершился с ошибкой.

    Example:
        >>> restore_dump_stream(["rclone", "cat", "yadisk:site-backup/db/db_2026.dump"])
    """
    ensure_pg_restore()
    logger.info("Восстановление БД из потока: %s", " ".join(source_command))
    pipe_commands(source_command, pg_restore_args(), env=pg_env())
    logger.info("База данных восстановлена")


def restore_db(source_arg: str, dump_name: str | None = None) -> None:
    """Восстановить БД из локального файла дампа либо из дампа цели.

    Args:
        source_arg (str): Путь к файлу дампа на диске либо имя цели;
            для цели берется последний дамп, если dump_name не задан.
        dump_name (str | None): Имя конкретного дампа в db/ цели.

    Raises:
        CommandError: Цель не определена, db/ цели недоступен либо
            восстановление завершилось с ошибкой.

    Example:
        >>> restore_db("OFFSITE")  # последний дамп цели OFFSITE
        >>> restore_db("/tmp/db_2026-08-25_1301.dump")  # локальный файл
        >>> restore_db("OFFSITE", dump_name="db_2026-08-24_2301.dump")
    """
    if Path(source_arg).is_file():
        restore_database(source_arg)
    else:
        target = resolve_target(source_arg)
        if not dump_name:
            try:
                target_dumps = dumps(target.address)
            except CommandError:
                msg = f"db/ цели {source_arg} недоступен"
                raise CommandError(msg) from None
            dump_name = latest_dump(target_dumps)
        logger.info("Дамп БД: %s (цель %s)", dump_name, source_arg)
        restore_dump_stream(dump_source_command(target.address, dump_name))
    logger.info("Проверка целостности (счетчики таблиц, примененные миграции) - скилл postgresql-restore")


# --- Медиа -------------------------------------------------------------------


def media_source_stats() -> tuple[int, int]:
    """Число и суммарный объем объектов медиа в хранилище.

    Returns:
        tuple[int, int]: Количество объектов и суммарный размер в байтах;
        источник - медиа-бакет при STORAGE_TYPE=s3 (rclone size) либо
        каталог MEDIA_ROOT (os.walk).
    """
    if is_s3():
        result = run_command(
            ["rclone", "size", "--json", media_rclone_address()],
            env=media_rclone_env(),
            capture=True,
        )
        try:
            stats = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            msg = f"некорректный вывод rclone size: {result.stdout!r}"
            raise CommandError(msg) from error
        return int(stats.get("count", 0)), int(stats.get("bytes", 0))
    count = 0
    size = 0
    for root, _dirs, files in os.walk(settings.MEDIA_ROOT):
        for name in files:
            count += 1
            size += (Path(root) / name).stat().st_size
    return count, size


def media_source_count() -> int:
    """Число объектов медиа в хранилище (см. media_source_stats)."""
    return media_source_stats()[0]


def verify_media(media_targets: list[str]) -> None:
    """Проверка медиа-целей: наличие содержимого storage/ и число объектов.

    Ошибка - пустой или недоступный storage/ цели при непустом источнике;
    любое расхождение числа объектов с источником - предупреждение
    в журнале: зеркало полное, расхождений быть не должно.

    Args:
        media_targets (list[str]): Имена медиа-целей.

    Raises:
        CommandError: Хотя бы одна цель без содержимого при непустом источнике.
    """
    failures = 0
    source_count = media_source_count()
    for name in media_targets:
        target = resolve_target(name)
        target_count = media_count(target.address)
        if source_count > 0 and target_count == 0:
            logger.info("Цель %s (медиа): пусто или недоступен storage/ при %s объектах источника", name, source_count)
            failures += 1
            continue
        if target_count != source_count:
            logger.info(
                "Цель %s (медиа): предупреждение - %s объектов против %s в источнике",
                name,
                target_count,
                source_count,
            )
        else:
            logger.info("Цель %s (медиа): %s объектов (источник: %s)", name, target_count, source_count)
    if failures:
        msg = f"проверка медиа-целей завершилась с ошибками: {failures}"
        raise CommandError(msg)
    logger.info("Проверка медиа-целей пройдена")


def backup_media(*, verify: bool = False) -> dict[str, Any] | None:
    """Зеркальная синхронизация медиа в цели либо проверка целей (verify=True).

    Список целей берется из BACKUP_MEDIA_TARGETS; при пустом списке
    копирование пропускается с записью в журнал, а проверка считается
    ошибкой. Синхронизация зеркальная: объекты, исчезнувшие из
    хранилища, удаляются из целей.

    Args:
        verify (bool): True - проверить существующее содержимое целей
            вместо синхронизации.

    Returns:
        dict[str, Any] | None: Данные для отчета (цели, число объектов
        и суммарный объем хранилища) при реальном запуске; None при
        проверке целей либо пустом списке целей.

    Raises:
        CommandError: При STORAGE_TYPE=s3 не заданы обязательные настройки;
            при verify=True цели не настроены либо проверка выявила ошибки;
            при синхронизации - отказ команды.

    Example:
        >>> backup_media()  # эквивалент: python backend/manage.py backup_media
        >>> backup_media(verify=True)  # эквивалент: backup_media --verify
    """
    require_media_env()
    media_targets = load_target_list(settings.BACKUP_MEDIA_TARGETS)
    if verify:
        if not media_targets:
            msg = "цели медиа не настроены: BACKUP_MEDIA_TARGETS пуст"
            raise CommandError(msg)
        verify_media(media_targets)
        return None
    if not media_targets:
        logger.info("Медиа не копируется: BACKUP_MEDIA_TARGETS пуст")
        return None
    resolved = [resolve_target(name) for name in media_targets]
    for target in resolved:
        logger.info("Синхронизация медиа в цель %s", target.describe())
        sync_media(target.address)
    count, size = media_source_stats()
    logger.info("Резервное копирование медиа завершено")
    return {
        "targets": [target.describe() for target in resolved],
        "count": count,
        "size": size,
    }


def restore_media(target_name: str) -> None:
    """Восстановить медиа из storage/ цели в хранилище.

    Копирование недеструктивное: файлы хранилища, отсутствующие в цели,
    не удаляются. Пустая цель - восстановление пропускается с записью
    в журнал.

    Args:
        target_name (str): Имя цели с резервной копией медиа.

    Raises:
        CommandError: При STORAGE_TYPE=s3 не заданы обязательные настройки,
            цель не определена либо копирование завершилось с ошибкой.

    Example:
        >>> restore_media("OFFSITE")  # эквивалент: python backend/manage.py restore_media OFFSITE
    """
    require_media_env()
    target = resolve_target(target_name)
    if media_count(target.address) == 0:
        logger.info("В цели %s нет медиа - восстановление пропущено", target_name)
        return
    logger.info("Источник: цель %s (%s/storage)", target_name, target.address)
    pull_media(target.address)
    logger.info("Медиа восстановлены")
