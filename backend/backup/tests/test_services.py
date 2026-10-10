"""Тесты оркестрации системы резервного копирования."""

import os
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from unittest import skipUnless

import boto3  # type: ignore[import-untyped]
import requests  # type: ignore[import-untyped]
from django.conf import settings
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from backup import services
from backup.tests.helpers import S3_AVAILABLE, MediaTestCaseMixin, pg_client_compatible

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

    @override_settings(BACKUP_MEDIA_TARGETS="")
    def test_verify_without_targets_raises(self) -> None:
        """Проверка целей медиа без их настройки - ошибка."""
        with self.assertRaisesMessage(CommandError, "цели медиа не настроены"):
            services.backup_media(verify=True)

    def test_sync_removes_missing_from_target(self) -> None:
        """Синхронизация удаляет из цели объекты, исчезнувшие из хранилища."""
        stored = self.target_root / "storage"
        stored.mkdir(parents=True)
        (stored / "stale.jpg").write_bytes(b"old")
        with self.media_settings():
            services.backup_media()
        self.assertFalse((stored / "stale.jpg").exists())


class TestVerifyMedia(MediaTestCaseMixin):
    """Тесты проверки медиа-целей verify_media."""

    def test_matching_target_reports_no_discrepancy(self) -> None:
        """Полное зеркало источника не дает предупреждения о расхождении."""
        with self.media_settings():
            services.backup_media()
            with self.assertLogs("backup.services", level="INFO") as logs:
                services.verify_media(["DISK"])
        self.assertFalse(any("предупреждение" in message for message in logs.output))

    def test_discrepancy_warns(self) -> None:
        """Любое расхождение числа объектов с источником - предупреждение."""
        stored = self.target_root / "storage"
        stored.mkdir(parents=True)
        (stored / "img1.jpg").write_bytes(b"image")
        (stored / "extra.jpg").write_bytes(b"extra")
        with self.media_settings(), self.assertLogs("backup.services", level="INFO") as logs:
            services.verify_media(["DISK"])
        self.assertTrue(any("предупреждение" in message for message in logs.output))


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


class TestMediaRoundTrip(MediaTestCaseMixin):
    """Полный цикл медиа: синхронизация в цель и восстановление из нее."""

    def test_backup_then_restore(self) -> None:
        """Файл переживает очистку хранилища и возвращается из цели."""
        with self.media_settings():
            services.backup_media()
            (self.media_root / "img1.jpg").unlink()
            self.assertFalse((self.media_root / "img1.jpg").exists())
            services.restore_media("DISK")
        self.assertTrue((self.media_root / "img1.jpg").exists())


@skipUnless(S3_AVAILABLE and settings.STORAGE_TYPE == "s3", "S3-хранилище недоступно")
class TestMediaS3RestoreKeepsPublic(SimpleTestCase):
    """Восстановление медиа из цели сохраняет публичность объектов."""

    def test_restore_keeps_objects_public(self) -> None:
        """После restore_media объект читается анонимно по URL хранилища.

        rclone не переносит ACL, поэтому загрузки восстановления идут
        с RCLONE_CONFIG_MEDIA_ACL=public-read; policy-серверы публичность
        дают политикой бакета. Анонимный запрос проверяет результат.
        """
        s3_options = settings.STORAGES["s3"]["OPTIONS"]
        client = boto3.client(
            "s3",
            aws_access_key_id=s3_options["access_key"],
            aws_secret_access_key=s3_options["secret_key"],
            endpoint_url=s3_options["endpoint_url"],
        )
        bucket = s3_options["bucket_name"]
        key = f"{settings.S3_MEDIA_LOCATION}/restore-public/{uuid.uuid4().hex[:8]}.jpg"
        client.put_object(Bucket=bucket, Key=key, Body=b"image")
        target_root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, target_root)
        self.addCleanup(client.delete_object, Bucket=bucket, Key=key)
        with override_settings(
            STORAGE_TYPE="s3",
            BACKUP_MEDIA_TARGETS="DISK",
            BACKUP_TARGETS={"DISK": str(target_root)},
        ):
            services.backup_media()
            client.delete_object(Bucket=bucket, Key=key)
            services.restore_media("DISK")
        url = f"{settings.AWS_S3_ENDPOINT_URL.rstrip('/')}/{bucket}/{key}"
        response = requests.get(url, timeout=10)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"image")


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
