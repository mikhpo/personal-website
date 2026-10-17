"""Тесты операций копирования инструментом rclone."""

import os
import shutil
import tempfile
import time
import unittest
import uuid
from pathlib import Path
from unittest import skipUnless

from django.test import SimpleTestCase

from backup import rclone
from backup.process import run_command

RCLONE = shutil.which("rclone")


@skipUnless(RCLONE, "rclone не установлен")
class TestRcloneOperations(SimpleTestCase):
    """Операции над адресом локальной цели реальным rclone."""

    def setUp(self) -> None:
        """Создать каталог цели и данные операций."""
        super().setUp()
        self.target = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Удалить временный каталог."""
        shutil.rmtree(self.target)
        super().tearDown()

    def test_push_and_list_dumps(self) -> None:
        """push_dump кладет дамп в db/ цели, dumps перечисляет его."""
        dump_path = self.target / "db_2026-10-11_2301.dump"
        dump_path.write_bytes(b"dump")
        rclone.push_dump(str(self.target), str(dump_path), dump_path.name)
        self.assertEqual(rclone.dumps(str(self.target)), [dump_path.name])

    def test_fresh_dump_detected_in_window(self) -> None:
        """Только что выгруженный дамп попадает в окно свежести."""
        dump_path = self.target / "db_2026-10-11_2302.dump"
        dump_path.write_bytes(b"dump")
        rclone.push_dump(str(self.target), str(dump_path), dump_path.name)
        self.assertTrue(rclone.has_fresh_dump(str(self.target)))

    def test_prune_dumps_removes_old(self) -> None:
        """prune_dumps удаляет дамп старше порога и сохраняет свежий."""
        old_name = f"db_2026-09-01_0000-{uuid.uuid4().hex[:4]}.dump"
        fresh_name = "db_2026-10-11_2303.dump"
        db_dir = self.target / "db"
        db_dir.mkdir(parents=True)
        (db_dir / old_name).write_bytes(b"old")
        (db_dir / fresh_name).write_bytes(b"fresh")
        old_age = time.time() - 20 * 86400
        os.utime(db_dir / old_name, (old_age, old_age))
        rclone.prune_dumps(str(self.target), 14)
        self.assertFalse((db_dir / old_name).exists())
        self.assertTrue((db_dir / fresh_name).exists())

    def test_media_count_counts_storage_tree(self) -> None:
        """media_count считает рекурсивно файлы storage/, каталог отсутствует - 0."""
        storage = self.target / "storage" / "album"
        storage.mkdir(parents=True)
        (storage / "img1.jpg").write_bytes(b"image")
        (self.target / "storage" / "img2.jpg").write_bytes(b"image")
        self.assertEqual(rclone.media_count(str(self.target)), 2)
        empty_target = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, empty_target)
        self.assertEqual(rclone.media_count(str(empty_target)), 0)

    def test_count_lines_counts_nonempty(self) -> None:
        """count_lines считает непустые строки захваченного вывода."""
        result = run_command(["printf", "a\nb\n\n"], capture=True)
        self.assertEqual(rclone.count_lines(result), 2)


if __name__ == "__main__":
    unittest.main()
