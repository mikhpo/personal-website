"""Общие помощники тестов резервного копирования."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import ClassVar
from unittest import skipUnless

from django.test import SimpleTestCase

from backup import services
from backup.targets import Target

RCLONE = shutil.which("rclone")
MC = shutil.which("mc")


class CallTarget(Target):
    """Плагин для тестов оркестрации: записывает вызовы вместо операций."""

    prefix = "call"
    created: ClassVar[list["CallTarget"]] = []

    def __init__(self, name: str, path: str) -> None:
        """Сохранить имя, путь и журнал вызовов."""
        super().__init__(name, path)
        self.calls: list[str] = []
        CallTarget.created.append(self)

    def sync_media(self) -> None:
        """Записать вызов синхронизации медиа."""
        self.calls.append("sync_media")

    def pull_media(self) -> None:
        """Записать вызов восстановления медиа."""
        self.calls.append("pull_media")

    def media_count(self) -> int:
        """Записать вызов; число объектов ненулевое, чтобы восстановление не пропускалось."""
        self.calls.append("media_count")
        return 1


def pg_client_compatible() -> bool:
    """Локальный клиент PostgreSQL совместим с сервером и доступен."""
    if not shutil.which("pg_dump"):
        return False
    env = {"PATH": os.environ.get("PATH", ""), **services.pg_env()}
    result = subprocess.run(
        ["pg_dump", "--schema-only", "-f", os.devnull],
        env=env,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


@skipUnless(MC, "MinIO Client (mc) не установлен")
@skipUnless(RCLONE, "rclone не установлен")
class MediaTestCaseMixin(SimpleTestCase):
    """Общая подготовка окружения для тестов медиа-операций."""

    def setUp(self) -> None:
        """Создать хранилище с файлом и каталог цели."""
        super().setUp()
        self.media_root = Path(tempfile.mkdtemp())
        (self.media_root / "img1.jpg").write_bytes(b"image")
        self.target_root = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Удалить временные каталоги."""
        shutil.rmtree(self.media_root)
        shutil.rmtree(self.target_root)
        super().tearDown()

    def media_settings(self) -> object:
        """Настройки медиа-операций для текущих каталогов."""
        return self.settings(
            MEDIA_ROOT=str(self.media_root),
            BACKUP_MEDIA_TARGETS="DISK",
            BACKUP_TARGETS={"DISK": f"rclone:{self.target_root}"},
            MC_PATH="mc",
            STORAGE_TYPE="filesystem",
        )
