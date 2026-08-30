"""Плагины-цели системы резервного копирования.

Цель - именованная запись BACKUP_TARGET_<ИМЯ> вида "<префикс>:<адрес>",
где префикс выбирает плагин из TARGET_PREFIXES. Новый механизм
копирования - подкласс Target с методами контракта и запись в
TARGET_PREFIXES; команды и оркестрация при этом не меняются.

Контракт плагина: push_dump, dumps, dump_source_command, prune_dumps,
has_fresh_dump, media_count, sync_media, pull_media.
"""

import re
import shutil
import subprocess

from django.conf import settings
from django.core.management.base import CommandError

from backup.process import run_command
from backup.utils import (
    mc_executable,
    media_mc_address,
    media_rclone_address,
    media_rclone_env,
)

FRESHNESS_WINDOW = "25h"
NAME_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")
MC_ADDRESS_RE = re.compile(r"^[^/]+/.+")


class Target:
    """Цель резервного копирования: имя и адрес хранилища.

    Attributes:
        prefix (str): Префикс инструмента цели ("mc", "rclone") - ключ
            реестра TARGET_PREFIXES; задается подклассом.
        name (str): Имя цели из настроек (заглавные буквы, цифры,
            подчеркивание), например "OFFSITE".
        path (str): Адрес хранилища цели в адресации инструмента:
            "alias/бакет[/префикс]" для mc, "remote:путь" или локальный
            путь для rclone.
    """

    prefix: str

    def __init__(self, name: str, path: str) -> None:
        """Сохранить имя цели и адрес хранилища.

        Args:
            name (str): Имя цели из настроек.
            path (str): Адрес хранилища цели.
        """
        self.name = name
        self.path = path

    def describe(self) -> str:
        """Человекочитаемое описание цели для отчетов и журналов.

        Returns:
            str: Строка вида "OFFSITE (mc: local/backups)".

        Example:
            >>> McTarget("OFFSITE", "local/backups").describe()
            'OFFSITE (mc: local/backups)'
        """
        return f"{self.name} ({self.prefix}: {self.path})"


def count_lines(result: subprocess.CompletedProcess[str]) -> int:
    r"""Число непустых строк захваченного вывода.

    Args:
        result (subprocess.CompletedProcess[str]): Результат команды
            со списком объектов (mc ls, rclone lsf).

    Returns:
        int: Количество непустых строк stdout; для вывода
        "img1.jpg\\nimg2.jpg\\n" вернет 2.

    Example:
        >>> result = run_command(["printf", "a\\nb\\n\\n"], capture=True)
        >>> count_lines(result)
        2
    """
    return len([line for line in (result.stdout or "").splitlines() if line.strip()])


class McTarget(Target):
    """Цель S3/MinIO через MinIO Client: alias/бакет[/префикс].

    Attributes:
        prefix (str): "mc".
        name (str): Имя цели из настроек.
        path (str): Адрес вида "local/backups": алиас mc "local", бакет
            "backups"; опциональный третий элемент - префикс внутри бакета.

    Example:
        Для записи в .env ``BACKUP_OFFSITE='mc:local/backups'`` цель
        создается методом resolve_target("OFFSITE"); дампы лежат в
        ``local/backups/db``, медиа - в ``local/backups/storage``.
    """

    prefix = "mc"

    def __init__(self, name: str, path: str) -> None:
        """Проверить вид адреса alias/бакет[/префикс] и наличие MinIO Client.

        Args:
            name (str): Имя цели из настроек.
            path (str): Адрес "alias/бакет[/префикс]".

        Raises:
            CommandError: Адрес не вида alias/бакет[/префикс], либо
                не задан MC_PATH / MinIO Client не найден.
        """
        super().__init__(name, path)
        if not MC_ADDRESS_RE.match(path):
            msg = f'спецификация mc-цели "{name}" должна иметь вид alias/бакет[/префикс]: "{path}"'
            raise CommandError(msg)
        mc_executable()

    def ensure_bucket(self) -> None:
        """Создать бакет адреса цели, если не существует.

        Raises:
            CommandError: Команда mb завершилась с ошибкой.
        """
        alias, _, rest = self.path.partition("/")
        bucket, _, _ = rest.partition("/")
        run_command([mc_executable(), "mb", "--ignore-existing", f"{alias}/{bucket}"])

    def push_dump(self, dump_path: str, dump_name: str) -> None:
        """Скопировать файл дампа в db/ цели, создав бакет при необходимости.

        Args:
            dump_path (str): Локальный путь к файлу дампа.
            dump_name (str): Имя файла дампа в db/ цели.

        Raises:
            CommandError: Копирование завершилось с ошибкой.
        """
        self.ensure_bucket()
        run_command([mc_executable(), "cp", dump_path, f"{self.path}/db/{dump_name}"])

    def dumps(self) -> list[str]:
        """Перечислить имена дампов в db/ цели.

        Returns:
            list[str]: Имена файлов дампов.

        Raises:
            CommandError: Листинг завершился с ошибкой (например, db/ недоступен).
        """
        result = run_command([mc_executable(), "ls", f"{self.path}/db"], capture=True)
        return [line.split()[-1] for line in (result.stdout or "").splitlines() if line.strip()]

    def dump_source_command(self, dump_name: str) -> list[str]:
        """Команда, выводящая дамп из db/ цели в stdout.

        Args:
            dump_name (str): Имя файла дампа.

        Returns:
            list[str]: Аргументы команды для pipe_commands или run_command.

        Example:
            >>> McTarget("OFFSITE", "local/backups").dump_source_command("db_2026.dump")
            ['mc', 'cat', 'local/backups/db/db_2026.dump']
        """
        return [mc_executable(), "cat", f"{self.path}/db/{dump_name}"]

    def prune_dumps(self, retention_days: int) -> None:
        """Удалить дампы старше retention_days дней из db/ цели.

        Args:
            retention_days (int): Срок хранения дампов в днях.

        Raises:
            CommandError: Удаление завершилось с ошибкой.
        """
        mc = mc_executable()
        run_command(
            [
                mc,
                "find",
                f"{self.path}/db",
                "--name",
                "*.dump",
                "--older-than",
                f"{retention_days}d",
                "--exec",
                f"{mc} rm {{}}",
            ],
        )

    def has_fresh_dump(self) -> bool:
        """Признак наличия в db/ цели дампа моложе окна свежести.

        Returns:
            bool: True, если за окно FRESHNESS_WINDOW появлялся *.dump.
        """
        result = run_command(
            [mc_executable(), "find", f"{self.path}/db", "--name", "*.dump", "--newer-than", FRESHNESS_WINDOW],
            capture=True,
        )
        return bool((result.stdout or "").strip())

    def media_count(self) -> int:
        """Число объектов в storage/ цели (0 при отсутствии storage/).

        Returns:
            int: Количество объектов; 0 также при недоступном storage/.
        """
        result = run_command([mc_executable(), "ls", "--recursive", f"{self.path}/storage"], capture=True, check=False)
        return count_lines(result)

    def sync_media(self) -> None:
        """Зеркально синхронизировать медиа-хранилище в storage/ цели.

        Зеркало удаляет из цели объекты, исчезнувшие из хранилища.

        Raises:
            CommandError: Синхронизация завершилась с ошибкой.
        """
        self.ensure_bucket()
        run_command(
            [mc_executable(), "mirror", "--overwrite", "--remove", media_mc_address(), f"{self.path}/storage"],
        )

    def pull_media(self) -> None:
        """Скопировать storage/ цели в медиа-хранилище без удаления лишних файлов.

        Raises:
            CommandError: Копирование завершилось с ошибкой.
        """
        run_command([mc_executable(), "mirror", "--overwrite", f"{self.path}/storage", media_mc_address()])


class RcloneTarget(Target):
    """Цель локального каталога или облачного хранилища через rclone.

    Attributes:
        prefix (str): "rclone".
        name (str): Имя цели из настроек.
        path (str): Локальный путь ("/mnt/backup") либо "remote:путь",
            где remote настроен в rclone.conf хоста (yandex, onedrive...).

    Example:
        Для записи в .env ``BACKUP_YADISK='rclone:yadisk:site-backup'``
        цель создается методом resolve_target("YADISK"); дампы лежат в
        ``yadisk:site-backup/db``, медиа - в ``yadisk:site-backup/storage``.
    """

    prefix = "rclone"

    def __init__(self, name: str, path: str) -> None:
        """Проверить наличие rclone.

        Args:
            name (str): Имя цели из настроек.
            path (str): Локальный путь или "remote:путь".

        Raises:
            CommandError: rclone не найден в PATH.
        """
        super().__init__(name, path)
        if not shutil.which("rclone"):
            msg = f'rclone-цель "{name}" требует установленный rclone'
            raise CommandError(msg)

    def push_dump(self, dump_path: str, dump_name: str) -> None:
        """Скопировать файл дампа в db/ цели.

        Args:
            dump_path (str): Локальный путь к файлу дампа.
            dump_name (str): Имя файла дампа в db/ цели.

        Raises:
            CommandError: Копирование завершилось с ошибкой.
        """
        run_command(["rclone", "copyto", dump_path, f"{self.path}/db/{dump_name}"])

    def dumps(self) -> list[str]:
        """Перечислить имена дампов в db/ цели.

        Returns:
            list[str]: Имена файлов дампов.

        Raises:
            CommandError: Листинг завершился с ошибкой (например, db/ недоступен).
        """
        result = run_command(["rclone", "lsf", "--files-only", f"{self.path}/db"], capture=True)
        return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]

    def dump_source_command(self, dump_name: str) -> list[str]:
        """Команда, выводящая дамп из db/ цели в stdout.

        Args:
            dump_name (str): Имя файла дампа.

        Returns:
            list[str]: Аргументы команды для pipe_commands или run_command.

        Example:
            >>> RcloneTarget("DISK", "/mnt/backup").dump_source_command("db_2026.dump")
            ['rclone', 'cat', '/mnt/backup/db/db_2026.dump']
        """
        return ["rclone", "cat", f"{self.path}/db/{dump_name}"]

    def prune_dumps(self, retention_days: int) -> None:
        """Удалить дампы старше retention_days дней из db/ цели.

        Args:
            retention_days (int): Срок хранения дампов в днях.

        Raises:
            CommandError: Удаление завершилось с ошибкой.
        """
        run_command(
            ["rclone", "delete", f"{self.path}/db", "--min-age", f"{retention_days}d", "--include", "*.dump"],
        )

    def has_fresh_dump(self) -> bool:
        """Признак наличия в db/ цели дампа моложе окна свежести.

        Returns:
            bool: True, если за окно FRESHNESS_WINDOW появлялся *.dump.
        """
        result = run_command(
            ["rclone", "lsf", "--files-only", "--max-age", FRESHNESS_WINDOW, "--include", "*.dump", f"{self.path}/db"],
            capture=True,
        )
        return bool((result.stdout or "").strip())

    def media_count(self) -> int:
        """Число объектов в storage/ цели (0 при отсутствии storage/).

        Returns:
            int: Количество объектов; 0 также при недоступном storage/.
        """
        result = run_command(
            ["rclone", "lsf", "--recursive", "--files-only", f"{self.path}/storage"],
            capture=True,
            check=False,
        )
        return count_lines(result)

    def sync_media(self) -> None:
        """Зеркально синхронизировать медиа-хранилище в storage/ цели.

        Зеркало удаляет из цели объекты, исчезнувшие из хранилища.
        При STORAGE_TYPE=s3 медиа-бакет открывается через remote media,
        собираемый из RCLONE_CONFIG_* (см. backup.utils.media_rclone_env).

        Raises:
            CommandError: Синхронизация завершилась с ошибкой.
        """
        run_command(["rclone", "sync", media_rclone_address(), f"{self.path}/storage"], env=media_rclone_env())

    def pull_media(self) -> None:
        """Скопировать storage/ цели в медиа-хранилище без удаления лишних файлов.

        Raises:
            CommandError: Копирование завершилось с ошибкой.
        """
        run_command(["rclone", "copy", f"{self.path}/storage", media_rclone_address()], env=media_rclone_env())


# Реестр плагинов: префикс спецификации цели -> класс плагина.
# Новый механизм копирования добавляется подклассом Target и записью
# в этот словарь, без правок оркестрации и команд.
TARGET_PREFIXES: dict[str, type[Target]] = {"mc": McTarget, "rclone": RcloneTarget}


def resolve_target(name: str) -> Target:
    """Разрешить имя цели в плагин по префиксу спецификации из настроек.

    Args:
        name (str): Имя цели, определенное записью BACKUP_TARGET_<ИМЯ> в .env.

    Returns:
        Target: Плагин цели (McTarget или RcloneTarget).

    Raises:
        CommandError: Недопустимое имя, цель не определена в .env, неизвестный
            префикс спецификации, пустая спецификация либо недоступен
            инструмент цели.

    Example:
        Для записи в .env ``BACKUP_OFFSITE='mc:local/backups'``:
        >>> target = resolve_target("OFFSITE")
        >>> target.prefix
        'mc'
        >>> target.path
        'local/backups'
    """
    if not NAME_RE.match(name):
        msg = f'недопустимое имя цели "{name}": имена целей - заглавные буквы, цифры и подчеркивание'
        raise CommandError(msg)
    spec = settings.BACKUP_TARGETS.get(name)
    if not spec:
        msg = f'цель "{name}" не определена: нет переменной BACKUP_TARGET_{name} в .env'
        raise CommandError(msg)
    prefix, _, path = spec.partition(":")
    target_cls = TARGET_PREFIXES.get(prefix)
    if target_cls is None:
        allowed = ", ".join(f"{item}:" for item in TARGET_PREFIXES)
        msg = f'неизвестный префикс цели "{name}": "{spec}" (допустимы: {allowed})'
        raise CommandError(msg)
    if not path:
        msg = f'пустая спецификация {prefix}-цели "{name}"'
        raise CommandError(msg)
    return target_cls(name, path)
