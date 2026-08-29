"""Тесты полезной логики подготовки данных системы резервного копирования."""

from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from backup.utils import (
    latest_dump,
    media_mc_address,
    media_rclone_address,
    media_rclone_env,
    pg_env,
    require_media_env,
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
    "MINIO_ALIAS": "local",
    "AWS_STORAGE_BUCKET_NAME": "media",
    "AWS_S3_ENDPOINT_URL": "http://minio:9000",
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
    """Тесты адресации медиа-хранилища для инструментов целей."""

    @override_settings(STORAGE_TYPE="filesystem", MEDIA_ROOT="/srv/storage")
    def test_filesystem_addresses_media_root(self) -> None:
        """При filesystem оба инструмента работают с MEDIA_ROOT без rclone-окружения."""
        self.assertEqual(media_mc_address(), "/srv/storage")
        self.assertEqual(media_rclone_address(), "/srv/storage")
        self.assertIsNone(media_rclone_env())

    @override_settings(**S3_SETTINGS)
    def test_s3_addresses_media_prefix(self) -> None:
        """При s3 mc адресует префикс media/ бакета, rclone - remote с RCLONE_CONFIG_*."""
        self.assertEqual(media_mc_address(), "local/media/media")
        self.assertEqual(media_rclone_address(), "media:media/media")
        self.assertEqual(
            media_rclone_env(),
            {
                "RCLONE_CONFIG_MEDIA_TYPE": "s3",
                "RCLONE_CONFIG_MEDIA_ENDPOINT": "http://minio:9000",
                "RCLONE_CONFIG_MEDIA_ACCESS_KEY_ID": "key",
                "RCLONE_CONFIG_MEDIA_SECRET_ACCESS_KEY": "secret",
                "RCLONE_CONFIG_MEDIA_REGION": "ru-central1",
            },
        )


class TestRequireMediaEnv(SimpleTestCase):
    """Тесты проверки обязательных настроек медиа."""

    @override_settings(STORAGE_TYPE="filesystem", MC_PATH="")
    def test_filesystem_requires_nothing(self) -> None:
        """При filesystem обязательные настройки S3 и MC_PATH не требуются."""
        require_media_env()

    @override_settings(
        STORAGE_TYPE="s3",
        MINIO_ALIAS="",
        AWS_STORAGE_BUCKET_NAME="",
        AWS_S3_ENDPOINT_URL="",
        AWS_ACCESS_KEY_ID="",
        AWS_SECRET_ACCESS_KEY="",
    )
    def test_s3_missing_vars_raise(self) -> None:
        """При s3 незаданные переменные S3 перечисляются в ошибке."""
        with self.assertRaisesMessage(CommandError, "MINIO_ALIAS"):
            require_media_env()
