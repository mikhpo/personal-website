"""Тесты фактического выполнения management-команд резервного копирования."""

import os
import shutil
import subprocess
import tempfile
import uuid
from io import StringIO
from pathlib import Path
from unittest import skipUnless

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase

from backup import services
from backup.tests.helpers import MediaTestCaseMixin, pg_client_compatible


class TestBackupMediaCommand(MediaTestCaseMixin):
    """Команда backup_media фактически зеркалирует медиа в цель."""

    def test_mirrors_media_to_target(self) -> None:
        """После вызова команды storage/ цели содержит файл хранилища."""
        with self.media_settings():
            call_command("backup_media", stdout=StringIO())
        stored = self.target_root / "storage"
        self.assertTrue((stored / "img1.jpg").exists())


class TestRestoreMediaCommand(MediaTestCaseMixin):
    """Команда restore_media фактически восстанавливает медиа из цели."""

    def test_restores_media_from_target(self) -> None:
        """После вызова команды файл возвращается в хранилище."""
        stored = self.target_root / "storage"
        stored.mkdir(parents=True)
        (stored / "img1.jpg").write_bytes(b"image")
        with self.media_settings():
            call_command("restore_media", "DISK", stdout=StringIO())
        self.assertTrue((self.media_root / "img1.jpg").exists())


@skipUnless(pg_client_compatible(), "локальный клиент PostgreSQL несовместим с сервером")
class TestBackupDbCommand(SimpleTestCase):
    """Команда backup_db фактически создаёт дамп БД в цели."""

    def setUp(self) -> None:
        """Создать каталоги бэкапа и цели."""
        self.backup_root = Path(tempfile.mkdtemp())
        self.target_root = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Удалить временные каталоги."""
        shutil.rmtree(self.backup_root)
        shutil.rmtree(self.target_root)

    def test_creates_dump_in_target(self) -> None:
        """После вызова команды в db/ цели появляется файл дампа."""
        with self.settings(
            BACKUP_ROOT=str(self.backup_root),
            BACKUP_DB_TARGETS="DISK",
            BACKUP_TARGETS={"DISK": f"rclone:{self.target_root}"},
            MC_PATH="mc",
            BACKUP_DB_RETENTION_DAYS=14,
        ):
            call_command("backup_db", stdout=StringIO())
        self.assertTrue(list((self.target_root / "db").glob("*.dump")))


@skipUnless(pg_client_compatible(), "локальный клиент PostgreSQL несовместим с сервером")
class TestBackupCommand(SimpleTestCase):
    """Команда backup фактически выполняет бэкап БД и медиа."""

    def setUp(self) -> None:
        """Создать хранилище и каталоги бэкапа и цели."""
        self.media_root = Path(tempfile.mkdtemp())
        (self.media_root / "img1.jpg").write_bytes(b"image")
        self.backup_root = Path(tempfile.mkdtemp())
        self.target_root = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Удалить временные каталоги."""
        shutil.rmtree(self.media_root)
        shutil.rmtree(self.backup_root)
        shutil.rmtree(self.target_root)

    def test_backs_up_db_and_media(self) -> None:
        """После вызова команды цель содержит дамп БД и зеркало медиа."""
        with self.settings(
            MEDIA_ROOT=str(self.media_root),
            BACKUP_ROOT=str(self.backup_root),
            BACKUP_DB_TARGETS="DISK",
            BACKUP_MEDIA_TARGETS="DISK",
            BACKUP_TARGETS={"DISK": f"rclone:{self.target_root}"},
            MC_PATH="mc",
            STORAGE_TYPE="filesystem",
            BACKUP_DB_RETENTION_DAYS=14,
        ):
            call_command("backup", stdout=StringIO())
        self.assertTrue(list((self.target_root / "db").glob("*.dump")))
        self.assertTrue((self.target_root / "storage" / "img1.jpg").exists())


@skipUnless(pg_client_compatible(), "локальный клиент PostgreSQL несовместим с сервером")
class TestRestoreDbCommand(SimpleTestCase):
    """Команда restore_db фактически восстанавливает базу данных."""

    def setUp(self) -> None:
        """Создать базу-источник, пустую базу-приёмник и каталог дампов."""
        self.backup_root = Path(tempfile.mkdtemp())
        self.src_db = f"backup_src_{uuid.uuid4().hex[:8]}"
        self.dst_db = f"backup_dst_{uuid.uuid4().hex[:8]}"
        main = settings.DATABASES["default"]["NAME"]
        env = {"PATH": os.environ.get("PATH", ""), **services.pg_env()}
        subprocess.run(["createdb", "-T", main, self.src_db], env=env, check=True, capture_output=True)
        subprocess.run(["createdb", self.dst_db], env=env, check=True, capture_output=True)
        self._src_config = {**settings.DATABASES["default"], "NAME": self.src_db}
        self._dst_config = {**settings.DATABASES["default"], "NAME": self.dst_db}

    def tearDown(self) -> None:
        """Удалить временные базы и каталог дампов."""
        env = {"PATH": os.environ.get("PATH", ""), **services.pg_env()}
        for name in (self.dst_db, self.src_db):
            subprocess.run(["dropdb", "--if-exists", name], env=env, check=True, capture_output=True)
        shutil.rmtree(self.backup_root)

    def test_restores_database_into_empty_db(self) -> None:
        """После вызова команды пустая база получает таблицы из дампа."""
        with self.settings(DATABASES={"default": self._src_config}, BACKUP_ROOT=str(self.backup_root)):
            _dump_name, dump_path = services.dump_database()
        with self.settings(DATABASES={"default": self._dst_config}):
            call_command("restore_db", dump_path, stdout=StringIO())
        env = {"PATH": os.environ.get("PATH", ""), "PGDATABASE": self.dst_db, **services.pg_env()}
        result = subprocess.run(
            ["psql", "-tAc", "select count(*) from information_schema.tables where table_schema='public'"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertGreater(int(result.stdout.strip()), 0)
