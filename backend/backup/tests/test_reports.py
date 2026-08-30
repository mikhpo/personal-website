"""Тесты отчетов о результатах резервного копирования."""

import shutil
import smtplib
import tempfile
from io import StringIO
from pathlib import Path
from typing import Any
from unittest import skipUnless

from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from backup.reports import STATUS_FAIL, format_count, format_duration, format_size
from backup.tests.helpers import MediaTestCaseMixin, pg_client_compatible

LOCMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
NOTIFY_SETTINGS = {
    "EMAIL_BACKEND": LOCMAIL_BACKEND,
    "BACKUP_NOTIFY_EMAIL": "admin@example.com",
    "DEFAULT_FROM_EMAIL": "site@example.com",
}


class FailingEmailBackend:
    """Почтовый backend, имитирующий отказ SMTP-сервера."""

    def __init__(self, **kwargs: object) -> None:
        """Принять параметры подключения Django без использования."""

    def send_messages(self, messages: list[Any]) -> int:  # noqa: ARG002
        """Отказать в отправке любого письма.

        Args:
            messages (list[Any]): Сообщения, подготовленные Django.

        Raises:
            SMTPException: Отказ доставки.
        """
        msg = "соединение с почтовым сервером не установлено"
        raise smtplib.SMTPException(msg)


class TestReportFormats(SimpleTestCase):
    """Форматирование объемов, чисел и длительностей отчета."""

    def test_format_size_russian_units(self) -> None:
        """Размеры выводятся с запятой-разделителем и единицами Б-ГБ."""
        self.assertEqual(format_size(5), "5,0 Б")
        self.assertEqual(format_size(1468006), "1,4 МБ")
        self.assertEqual(format_size(int(15.8 * 1024**3)), "15,8 ГБ")

    def test_format_count_thousands_separator(self) -> None:
        """Числа объектов выводятся с пробелами между разрядами."""
        self.assertEqual(format_count(6707), "6 707")
        self.assertEqual(format_count(1), "1")

    def test_format_duration_minutes_and_seconds(self) -> None:
        """Длительность выводится в минутах и секундах."""
        self.assertEqual(format_duration(754), "12 мин 34 с")
        self.assertEqual(format_duration(42), "0 мин 42 с")

    def test_format_duration_with_hours(self) -> None:
        """Часы добавляются только при длительности более часа."""
        self.assertEqual(format_duration(3754), "1 ч 2 мин 34 с")


@override_settings(**NOTIFY_SETTINGS)
class TestBackupMediaReport(MediaTestCaseMixin):
    """Команда backup_media отправляет отчет об успешной синхронизации."""

    def test_sends_success_report_with_media_section(self) -> None:
        """В письме - тема с командой и статусом, раздел «Медиа» и цель."""
        with self.media_settings():
            call_command("backup_media", stdout=StringIO())
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertTrue(message.subject.startswith("[personal-website] Бэкап: успех - backup_media"))
        assert isinstance(message, EmailMultiAlternatives)
        html = str(message.alternatives[0][0])
        self.assertIn("Резервное копирование", html)
        self.assertIn("#e6f4ea", html)
        self.assertIn("Медиа", html)
        self.assertIn("DISK (rclone:", html)
        self.assertIn("Объектов", html)
        self.assertIn("5,0 Б", html)

    def test_verify_does_not_send_report(self) -> None:
        """Проверка целей (--verify) уведомлений не создает."""
        stored = self.target_root / "storage"
        stored.mkdir(parents=True)
        (stored / "img1.jpg").write_bytes(b"image")
        with self.media_settings():
            call_command("backup_media", "--verify", stdout=StringIO())
        self.assertEqual(len(mail.outbox), 0)


@override_settings(**{**NOTIFY_SETTINGS, "BACKUP_NOTIFY_EMAIL": ""})
class TestNotifyDisabled(MediaTestCaseMixin):
    """Пустой BACKUP_NOTIFY_EMAIL отключает рассылку отчетов."""

    def test_no_email_without_recipient(self) -> None:
        """Реальный запуск без получателя выполняется без писем."""
        with self.media_settings():
            call_command("backup_media", stdout=StringIO())
        self.assertTrue((self.target_root / "storage" / "img1.jpg").exists())
        self.assertEqual(len(mail.outbox), 0)


@override_settings(**NOTIFY_SETTINGS)
class TestBackupMediaErrorReport(MediaTestCaseMixin):
    """Ошибка операции дает письмо со статусом ОШИБКА и журналом."""

    def test_sends_error_report_with_journal(self) -> None:
        """Команда не падает, в письме - журнал и текст ошибки."""
        with (
            self.media_settings(),
            override_settings(
                STORAGE_TYPE="s3",
                MINIO_ALIAS=None,
                AWS_STORAGE_BUCKET_NAME=None,
                AWS_S3_ENDPOINT_URL=None,
                AWS_ACCESS_KEY_ID=None,
                AWS_SECRET_ACCESS_KEY=None,
            ),
        ):
            call_command("backup_media", stdout=StringIO())
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertIn(STATUS_FAIL, message.subject)
        assert isinstance(message, EmailMultiAlternatives)
        html = str(message.alternatives[0][0])
        self.assertIn("#fce8e6", html)
        self.assertIn("Журнал команды:", html)
        self.assertIn("не задана в .env", html)


@override_settings(**NOTIFY_SETTINGS)
@skipUnless(pg_client_compatible(), "локальный клиент PostgreSQL несовместим с сервером")
class TestBackupDbReport(SimpleTestCase):
    """Команда backup_db отправляет отчет с разделом «База данных»."""

    def setUp(self) -> None:
        """Создать каталоги бэкапа и цели."""
        self.backup_root = Path(tempfile.mkdtemp())
        self.target_root = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Удалить временные каталоги."""
        shutil.rmtree(self.backup_root)
        shutil.rmtree(self.target_root)

    def test_sends_success_report_with_db_section(self) -> None:
        """В письме - цель, дамп, объем и ретеншн."""
        with self.settings(
            BACKUP_ROOT=str(self.backup_root),
            BACKUP_DB_TARGETS="DISK",
            BACKUP_TARGETS={"DISK": f"rclone:{self.target_root}"},
            MC_PATH="mc",
            BACKUP_DB_RETENTION_DAYS=14,
        ):
            call_command("backup_db", stdout=StringIO())
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertTrue(message.subject.startswith("[personal-website] Бэкап: успех - backup_db"))
        assert isinstance(message, EmailMultiAlternatives)
        html = str(message.alternatives[0][0])
        self.assertIn("База данных", html)
        self.assertIn("DISK (rclone:", html)
        self.assertIn(".dump", html)
        self.assertIn("дампы старше 14 дней удалены", html)


@override_settings(
    EMAIL_BACKEND="backup.tests.test_reports.FailingEmailBackend",
    BACKUP_NOTIFY_EMAIL="admin@example.com",
    DEFAULT_FROM_EMAIL="site@example.com",
)
class TestSendFailureDoesNotFail(MediaTestCaseMixin):
    """Отказ SMTP не меняет результат команды."""

    def test_command_succeeds_when_smtp_fails(self) -> None:
        """Бэкап выполнен, ошибка отправки пишется предупреждением."""
        with (
            self.media_settings(),
            self.assertLogs("backup.reports", level="WARNING"),
        ):
            call_command("backup_media", stdout=StringIO())
        self.assertTrue((self.target_root / "storage" / "img1.jpg").exists())
