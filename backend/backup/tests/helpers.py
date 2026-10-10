"""Общие помощники тестов резервного копирования."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest import skipUnless

from django.test import SimpleTestCase

from backup import services

RCLONE = shutil.which("rclone")


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
            BACKUP_TARGETS={"DISK": str(self.target_root)},
            STORAGE_TYPE="filesystem",
        )
