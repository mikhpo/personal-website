"""Тесты оркестрации системы резервного копирования."""

import os
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from unittest import skipUnless

from django.conf import settings
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from backup import services
from backup.process import run_command
from backup.targets import TARGET_PREFIXES
from backup.tests.helpers import CallTarget, MediaTestCaseMixin, pg_client_compatible

OLD_AGE_DAYS = 20
SECONDS_PER_DAY = 86400


class TestApplyLocalRetention(SimpleTestCase):
    """Тесты функции apply_local_retention."""

    def setUp(self) -> None:
        """Создать каталог db с устаревшим и свежим дампами."""
        self.root = Path(tempfile.mkdtemp())
        self.db_dir = self.root / "db"
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.old_dump = self.db_dir / "old.dump"
        self.old_dump.write_bytes(b"x")
        os.utime(self.old_dump, (time.time() - OLD_AGE_DAYS * SECONDS_PER_DAY,) * 2)
        self.fresh_dump = self.db_dir / "fresh.dump"
        self.fresh_dump.write_bytes(b"y")

    def tearDown(self) -> None:
        """Удалить временные файлы."""
        for entry in self.db_dir.iterdir():
            entry.unlink()
        self.db_dir.rmdir()
        self.root.rmdir()

    def test_removes_old_and_keeps_fresh(self) -> None:
        """Ретеншн удаляет устаревший дамп и сохраняет свежий."""
        services.apply_local_retention(str(self.root), 14)
        self.assertFalse(self.old_dump.exists())
        self.assertTrue(self.fresh_dump.exists())

    def test_keeps_non_dump_files(self) -> None:
        """Ретеншн не трогает файлы вне дампов."""
        notes = self.db_dir / "notes.txt"
        notes.write_bytes(b"x")
        services.apply_local_retention(str(self.root), 14)
        self.assertTrue(notes.exists())


class TestBackupDb(SimpleTestCase):
    """Тесты функции backup_db."""

    @override_settings(BACKUP_DB_TARGETS="")
    def test_verify_without_targets_raises(self) -> None:
        """Проверка целей БД без их настройки - ошибка."""
        with self.assertRaisesMessage(CommandError, "цели БД не настроены"):
            services.backup_db(verify=True)


class TestBackupMedia(MediaTestCaseMixin):
    """Тесты функции backup_media."""

    def test_mirrors_to_target(self) -> None:
        """Бэкап медиа копирует storage/ в цель."""
        with self.media_settings():
            services.backup_media()
        stored = self.target_root / "storage"
        self.assertTrue((stored / "img1.jpg").exists())

    @override_settings(BACKUP_MEDIA_TARGETS="", MC_PATH="mc")
    def test_verify_without_targets_raises(self) -> None:
        """Проверка целей медиа без их настройки - ошибка."""
        with self.assertRaisesMessage(CommandError, "цели медиа не настроены"):
            services.backup_media(verify=True)

    def test_overwrite_and_remove_flags(self) -> None:
        """Mc mirror с флагами --overwrite и --remove заменяет и удаляет лишнее."""
        mc = shutil.which("mc")
        assert mc is not None
        (self.media_root / "keep.jpg").write_bytes(b"newer-longer-content")
        (self.target_root / "keep.jpg").write_bytes(b"older")
        (self.target_root / "stale.jpg").write_bytes(b"old")
        run_command([mc, "mirror", "--overwrite", "--remove", str(self.media_root), str(self.target_root)])
        self.assertEqual((self.target_root / "keep.jpg").read_bytes(), b"newer-longer-content")
        self.assertFalse((self.target_root / "stale.jpg").exists())


class TestRestoreMedia(MediaTestCaseMixin):
    """Тесты функции restore_media."""

    def test_copies_from_target(self) -> None:
        """Восстановление медиа возвращает файлы из storage/ цели."""
        stored = self.target_root / "storage"
        stored.mkdir(parents=True)
        (stored / "img1.jpg").write_bytes(b"image")
        with self.media_settings():
            services.restore_media("DISK")
        self.assertTrue((self.media_root / "img1.jpg").exists())


class TestPluginMediaBackup(SimpleTestCase):
    """Оркестрация медиа работает с любым плагином из реестра."""

    def test_backup_and_restore_through_registered_plugin(self) -> None:
        """Бэкап и восстановление медиа идут через методы зарегистрированного плагина."""
        TARGET_PREFIXES["call"] = CallTarget
        self.addCleanup(TARGET_PREFIXES.pop, "call")
        CallTarget.created.clear()
        with override_settings(
            STORAGE_TYPE="filesystem",
            MEDIA_ROOT="/tmp/media",
            BACKUP_MEDIA_TARGETS="CALL",
            BACKUP_TARGETS={"CALL": "call:host/path"},
        ):
            services.backup_media()
            services.restore_media("CALL")
        self.assertEqual(len(CallTarget.created), 2)
        self.assertEqual(CallTarget.created[0].calls, ["sync_media"])
        self.assertEqual(CallTarget.created[1].calls, ["media_count", "pull_media"])


@skipUnless(pg_client_compatible(), "локальный клиент PostgreSQL несовместим с сервером")
class TestDbRoundTrip(SimpleTestCase):
    """Фактическое создание и восстановление дампа базы данных."""

    def setUp(self) -> None:
        """Создать базу-шаблон для дампа."""
        self.backup_root = Path(tempfile.mkdtemp())
        self.db_name = f"backup_test_{uuid.uuid4().hex[:8]}"
        self._db_config = {**settings.DATABASES["default"], "NAME": self.db_name}
        env = {"PATH": os.environ.get("PATH", ""), **services.pg_env()}
        subprocess.run(
            ["createdb", "-T", settings.DATABASES["default"]["NAME"], self.db_name],
            env=env,
            check=True,
            capture_output=True,
        )

    def tearDown(self) -> None:
        """Удалить временную базу и каталог дампов."""
        env = {"PATH": os.environ.get("PATH", ""), **services.pg_env()}
        subprocess.run(["dropdb", "--if-exists", self.db_name], env=env, check=True, capture_output=True)
        shutil.rmtree(self.backup_root)

    def test_dump_then_restore(self) -> None:
        """Дамп создаётся на диске и восстанавливается обратно в базу."""
        with self.settings(DATABASES={"default": self._db_config}, BACKUP_ROOT=str(self.backup_root)):
            dump_name, dump_path = services.dump_database()
            self.assertTrue(Path(dump_path).exists())
            self.assertTrue(dump_name.endswith(".dump"))
            services.restore_database(dump_path)
