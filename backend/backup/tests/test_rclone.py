"""Тесты операций копирования инструментом rclone."""

import os
import shutil
import tempfile
import time
from pathlib import Path
from unittest import skipUnless

from django.core.management.base import CommandError
from django.test import SimpleTestCase

from backup import rclone
from backup.process import run_command

RCLONE = shutil.which("rclone")


@skipUnless(RCLONE, "rclone не установлен")
class TestCountLines(SimpleTestCase):
    """Тесты подсчета непустых строк захваченного вывода."""

    def test_counts_nonempty_lines(self) -> None:
        """Пустые строки вывода не считаются."""
        result = run_command(["printf", "a\nb\n\n"], capture=True)
        self.assertEqual(rclone.count_lines(result), 2)


class RcloneTargetTestCase(SimpleTestCase):
    """Общий каталог-цель для тестов операций над адресом."""

    def setUp(self) -> None:
        """Создать каталог цели."""
        super().setUp()
        self.target = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Удалить временный каталог."""
        shutil.rmtree(self.target)
        super().tearDown()


@skipUnless(RCLONE, "rclone не установлен")
class TestPushDump(RcloneTargetTestCase):
    """Тесты выгрузки дампа в db/ цели."""

    def test_puts_dump_into_target_db(self) -> None:
        """Дамп появляется в db/ цели под своим именем."""
        dump_path = self.target / "db_2026-10-11_2301.dump"
        dump_path.write_bytes(b"dump")
        rclone.push_dump(str(self.target), str(dump_path), dump_path.name)
        self.assertTrue((self.target / "db" / dump_path.name).is_file())


@skipUnless(RCLONE, "rclone не установлен")
class TestDumps(RcloneTargetTestCase):
    """Тесты листинга дампов db/ цели."""

    def test_lists_files_of_target_db(self) -> None:
        """Листинг возвращает имена всех файлов db/ цели."""
        db_dir = self.target / "db"
        db_dir.mkdir(parents=True)
        (db_dir / "a.dump").write_bytes(b"a")
        (db_dir / "notes.txt").write_bytes(b"b")
        self.assertEqual(rclone.dumps(str(self.target)), ["a.dump", "notes.txt"])


@skipUnless(RCLONE, "rclone не установлен")
class TestHasFreshDump(RcloneTargetTestCase):
    """Тесты окна свежести дампов цели."""

    def test_fresh_dump_detected(self) -> None:
        """Только что созданный дамп попадает в окно свежести."""
        db_dir = self.target / "db"
        db_dir.mkdir(parents=True)
        (db_dir / "db_2026-10-11_2302.dump").write_bytes(b"dump")
        self.assertTrue(rclone.has_fresh_dump(str(self.target)))

    def test_missing_db_raises_unavailable(self) -> None:
        """Отсутствующий db/ цели - ошибка недоступности (на нее опирается verify)."""
        with self.assertRaises(CommandError):
            rclone.has_fresh_dump(str(self.target))


@skipUnless(RCLONE, "rclone не установлен")
class TestPruneDumps(RcloneTargetTestCase):
    """Тесты ретеншна дампов цели."""

    def test_removes_old_keeps_fresh(self) -> None:
        """Дамп старше порога удаляется, свежий сохраняется."""
        db_dir = self.target / "db"
        db_dir.mkdir(parents=True)
        old_dump = db_dir / "db_2026-09-01_0000.dump"
        fresh_dump = db_dir / "db_2026-10-11_2303.dump"
        old_dump.write_bytes(b"old")
        fresh_dump.write_bytes(b"fresh")
        old_age = time.time() - 20 * 86400
        os.utime(old_dump, (old_age, old_age))
        rclone.prune_dumps(str(self.target), 14)
        self.assertFalse(old_dump.exists())
        self.assertTrue(fresh_dump.exists())


@skipUnless(RCLONE, "rclone не установлен")
class TestMediaCount(RcloneTargetTestCase):
    """Тесты подсчета объектов storage/ цели."""

    def test_counts_storage_tree_recursively(self) -> None:
        """Файлы подкаталогов storage/ считаются вместе с корневыми."""
        album_dir = self.target / "storage" / "album"
        album_dir.mkdir(parents=True)
        (album_dir / "img1.jpg").write_bytes(b"image")
        (self.target / "storage" / "img2.jpg").write_bytes(b"image")
        self.assertEqual(rclone.media_count(str(self.target)), 2)

    def test_missing_storage_counts_zero(self) -> None:
        """Отсутствие storage/ дает ноль, а не ошибку."""
        self.assertEqual(rclone.media_count(str(self.target)), 0)
