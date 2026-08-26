"""Тесты плагинов-целей системы резервного копирования."""

import shutil
from unittest import skipUnless

from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from backup.targets import (
    TARGET_PREFIXES,
    McTarget,
    RcloneTarget,
    resolve_target,
)
from backup.tests.helpers import CallTarget


class TestResolveTarget(SimpleTestCase):
    """Тесты разрешения имени цели в плагин."""

    @override_settings(MC_PATH="mc", BACKUP_TARGETS={"BUCKET": "mc:local/backups"})
    @skipUnless(shutil.which("mc"), "MinIO Client (mc) не установлен")
    def test_resolve_mc(self) -> None:
        """mc-цель разрешается в McTarget со спецификацией alias/бакет."""
        target = resolve_target("BUCKET")
        self.assertIsInstance(target, McTarget)
        self.assertEqual(target.name, "BUCKET")
        self.assertEqual(target.prefix, "mc")
        self.assertEqual(target.path, "local/backups")

    @override_settings(BACKUP_TARGETS={"DISK": "rclone:/mnt/backup"})
    @skipUnless(shutil.which("rclone"), "rclone не установлен")
    def test_resolve_rclone(self) -> None:
        """rclone-цель разрешается в RcloneTarget со спецификацией пути."""
        target = resolve_target("DISK")
        self.assertIsInstance(target, RcloneTarget)
        self.assertEqual(target.prefix, "rclone")
        self.assertEqual(target.path, "/mnt/backup")

    @override_settings(BACKUP_TARGETS={})
    def test_unknown_name_raises(self) -> None:
        """Незаписанное имя цели - ошибка."""
        with self.assertRaisesMessage(CommandError, "не определена"):
            resolve_target("NOWHERE")

    def test_invalid_name_raises(self) -> None:
        """Имя из строчных букв - ошибка."""
        with self.assertRaisesMessage(CommandError, "недопустимое имя цели"):
            resolve_target("disk")

    @override_settings(BACKUP_TARGETS={"FTP": "ftp://example.com/backup"})
    def test_unknown_prefix_raises(self) -> None:
        """Спецификация с префиксом без плагина - ошибка."""
        with self.assertRaisesMessage(CommandError, "неизвестный префикс"):
            resolve_target("FTP")

    @override_settings(MC_PATH="mc", BACKUP_TARGETS={"BUCKET": "mc:backups"})
    def test_mc_spec_requires_bucket(self) -> None:
        """Спецификация mc-цели без бакета - ошибка."""
        with self.assertRaisesMessage(CommandError, "должна иметь вид alias/бакет"):
            resolve_target("BUCKET")

    @override_settings(BACKUP_TARGETS={"EMPTY": "rclone:"})
    @skipUnless(shutil.which("rclone"), "rclone не установлен")
    def test_empty_spec_raises(self) -> None:
        """Пустая спецификация цели - ошибка."""
        with self.assertRaisesMessage(CommandError, "пустая спецификация"):
            resolve_target("EMPTY")


class TestRegistry(SimpleTestCase):
    """Тесты реестра префиксов: подключение плагина без правок оркестрации."""

    def test_new_plugin_resolves_by_prefix(self) -> None:
        """Плагин, добавленный в TARGET_PREFIXES, разрешается по своему префиксу."""
        TARGET_PREFIXES["call"] = CallTarget
        self.addCleanup(TARGET_PREFIXES.pop, "call")
        with override_settings(BACKUP_TARGETS={"CALL": "call:host/path"}):
            target = resolve_target("CALL")
        self.assertIsInstance(target, CallTarget)
        self.assertEqual(target.path, "host/path")
