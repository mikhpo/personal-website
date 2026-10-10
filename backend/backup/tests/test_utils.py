"""Тесты полезной логики подготовки данных системы резервного копирования."""

import shutil
from unittest import skipUnless

from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from backup.utils import (
    BackupTarget,
    latest_dump,
    media_rclone_address,
    media_rclone_env,
    pg_env,
    require_media_env,
    resolve_target,
)

DB_CONFIG = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mydb",
        "USER": "user",
        "PASSWORD": "secret",
        "HOST": "dbhost",
        "PORT": "5432",
        "OPTIONS": {"sslmode": "prefer", "sslrootcert": "/certs/root.crt"},
    },
}

S3_SETTINGS = {
    "STORAGE_TYPE": "s3",
    "AWS_STORAGE_BUCKET_NAME": "media",
    "AWS_S3_ENDPOINT_URL": "http://s3:9000",
    "AWS_ACCESS_KEY_ID": "key",
    "AWS_SECRET_ACCESS_KEY": "secret",
    "AWS_S3_REGION_NAME": "ru-central1",
}


class TestDumpHelpers(SimpleTestCase):
    """Тесты выбора дампа для восстановления."""

    def test_latest_dump(self) -> None:
        """Последний дамп выбирается по лексикографическому порядку имени."""
        names = ["db_2026-08-20_1200.dump", "db_2026-08-21_0800.dump"]
        self.assertEqual(latest_dump(names), "db_2026-08-21_0800.dump")


class TestBackupTarget(SimpleTestCase):
    """Тесты значения цели резервного копирования."""

    def test_describe(self) -> None:
        """Описание цели - имя и адрес."""
        self.assertEqual(BackupTarget("OFFSITE", "yadisk:site-backup").describe(), "OFFSITE (yadisk:site-backup)")


class TestResolveTarget(SimpleTestCase):
    """Тесты разрешения имени цели в адрес rclone."""

    @override_settings(BACKUP_TARGETS={"DISK": "/mnt/backup", "YADISK": "yadisk:site-backup"})
    @skipUnless(shutil.which("rclone"), "rclone не установлен")
    def test_resolve_returns_address(self) -> None:
        """Цель разрешается в имя и адрес из настроек без изменений."""
        local = resolve_target("DISK")
        self.assertEqual((local.name, local.address), ("DISK", "/mnt/backup"))
        remote = resolve_target("YADISK")
        self.assertEqual((remote.name, remote.address), ("YADISK", "yadisk:site-backup"))

    @override_settings(BACKUP_TARGETS={})
    def test_unknown_name_raises(self) -> None:
        """Незаписанное имя цели - ошибка."""
        with self.assertRaisesMessage(CommandError, "не определена"):
            resolve_target("NOWHERE")

    def test_invalid_name_raises(self) -> None:
        """Имя из строчных букв - ошибка."""
        with self.assertRaisesMessage(CommandError, "недопустимое имя цели"):
            resolve_target("disk")


class TestPgEnv(SimpleTestCase):
    """Тесты сбора переменных libpq из настроек подключения."""

    @override_settings(DATABASES=DB_CONFIG)
    def test_pg_env_builds_connection_variables(self) -> None:
        """PG*-переменные для pg_dump/pg_restore собираются из настроек БД, включая SSL."""
        pg = pg_env()
        self.assertEqual(pg["PGHOST"], "dbhost")
        self.assertEqual(pg["PGDATABASE"], "mydb")
        self.assertEqual(pg["PGUSER"], "user")
        self.assertEqual(pg["PGSSLMODE"], "prefer")
        self.assertEqual(pg["PGSSLROOTCERT"], "/certs/root.crt")


class TestMediaAddress(SimpleTestCase):
    """Тесты адресации медиа-хранилища для rclone."""

    @override_settings(STORAGE_TYPE="filesystem", MEDIA_ROOT="/srv/storage")
    def test_filesystem_addresses_media_root(self) -> None:
        """При filesystem rclone работает с MEDIA_ROOT без окружения remote."""
        self.assertEqual(media_rclone_address(), "/srv/storage")
        self.assertIsNone(media_rclone_env())

    @override_settings(**S3_SETTINGS)
    def test_s3_addresses_media_prefix(self) -> None:
        """При s3 rclone адресует префикс media/ бакета remote-ом с RCLONE_CONFIG_*."""
        self.assertEqual(media_rclone_address(), "media:media/media")
        self.assertEqual(
            media_rclone_env(),
            {
                "RCLONE_CONFIG_MEDIA_TYPE": "s3",
                "RCLONE_CONFIG_MEDIA_PROVIDER": "Other",
                "RCLONE_CONFIG_MEDIA_ENDPOINT": "http://s3:9000",
                "RCLONE_CONFIG_MEDIA_ACCESS_KEY_ID": "key",
                "RCLONE_CONFIG_MEDIA_SECRET_ACCESS_KEY": "secret",
                "RCLONE_CONFIG_MEDIA_REGION": "ru-central1",
                "RCLONE_CONFIG_MEDIA_ACL": "public-read",
            },
        )


class TestRequireMediaEnv(SimpleTestCase):
    """Тесты проверки обязательных настроек медиа."""

    @override_settings(STORAGE_TYPE="filesystem")
    def test_filesystem_requires_nothing(self) -> None:
        """При filesystem обязательные настройки S3 не требуются."""
        require_media_env()

    @override_settings(
        STORAGE_TYPE="s3",
        AWS_STORAGE_BUCKET_NAME="",
        AWS_S3_ENDPOINT_URL="",
        AWS_ACCESS_KEY_ID="",
        AWS_SECRET_ACCESS_KEY="",
    )
    def test_s3_missing_vars_raise(self) -> None:
        """При s3 незаданные переменные S3 перечисляются в ошибке."""
        with self.assertRaisesMessage(CommandError, "AWS_STORAGE_BUCKET_NAME"):
            require_media_env()
