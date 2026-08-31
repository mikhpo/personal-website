"""Тесты запуска внешних команд системы резервного копирования."""

from pathlib import Path

from django.core.management.base import CommandError
from django.test import SimpleTestCase

from backup.process import pipe_commands, run_command

TEST_TMP = "/tmp/backup-tests"


class TestRunCommand(SimpleTestCase):
    """Тесты запуска внешних команд."""

    @classmethod
    def setUpClass(cls) -> None:
        """Создать временный каталог тестов."""
        super().setUpClass()
        Path(TEST_TMP).mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Удалить временный каталог тестов."""
        for entry in Path(TEST_TMP).iterdir():
            entry.unlink()
        Path(TEST_TMP).rmdir()
        super().tearDownClass()

    def test_copies_file(self) -> None:
        """Команда копирования файла реально копирует файл."""
        source = Path(TEST_TMP) / "src.txt"
        dest = Path(TEST_TMP) / "dst.txt"
        source.write_text("содержимое", encoding="utf-8")
        run_command(["cp", str(source), str(dest)])
        self.assertTrue(dest.exists())
        self.assertEqual(dest.read_text(encoding="utf-8"), "содержимое")

    def test_capture_returns_stdout(self) -> None:
        """При capture=True вывод захватывается в результат."""
        result = run_command(["echo", "hello"], capture=True)
        self.assertIn("hello", result.stdout)

    def test_nonzero_exit_raises(self) -> None:
        """Завершение с ненулевым кодом бросает CommandError."""
        with self.assertRaises(CommandError):
            run_command(["false"])

    def test_nonzero_exit_with_check_false(self) -> None:
        """При check=False завершение с ошибкой не бросает исключение."""
        result = run_command(["false"], check=False)
        self.assertNotEqual(result.returncode, 0)

    def test_missing_command_raises(self) -> None:
        """Несуществующая команда - ошибка."""
        with self.assertRaisesMessage(CommandError, "команда не найдена"):
            run_command(["no-such-command-xyz"])


class TestPipeCommands(SimpleTestCase):
    """Тесты конвейера команд без временных файлов."""

    def test_streams_source_to_dest(self) -> None:
        """Вывод источника передается получателю через канал."""
        result = pipe_commands(["echo", "hello"], ["wc", "-c"])
        self.assertIn("6", result.stdout)

    def test_source_failure_raises(self) -> None:
        """Аварийное завершение источника - ошибка конвейера."""
        with self.assertRaisesMessage(CommandError, "конвейер"):
            pipe_commands(["false"], ["cat"])

    def test_dest_failure_raises(self) -> None:
        """Аварийное завершение получателя - ошибка конвейера."""
        with self.assertRaisesMessage(CommandError, "конвейер"):
            pipe_commands(["echo", "x"], ["false"])

    def test_source_sigpipe_with_dest_success(self) -> None:
        """Завершение источника по SIGPIPE при успешном получателе - не ошибка.

        Получатель вправе остановить чтение до конца потока (pg_restore -l
        читает только заголовок и оглавление дампа); источник получает
        SIGPIPE после этого - штатная семантика конвейера. Оболочка
        сообщает такой код как 141 (128 + номер сигнала), прямой потомок
        получает сигнал (-13) - проверяются обе формы.
        """
        result = pipe_commands(
            ["/bin/sh", "-c", "dd if=/dev/zero bs=1M count=8 2>/dev/null"],
            ["head", "-c", "1"],
        )
        self.assertEqual(result.returncode, 0)
        result = pipe_commands(
            ["python3", "-c", "import sys; sys.stdout.buffer.write(b'x' * 8192)"],
            ["head", "-c", "1"],
        )
        self.assertEqual(result.returncode, 0)

    def test_dest_failure_with_source_sigpipe_raises(self) -> None:
        """SIGPIPE источника не маскирует ошибку получателя."""
        with self.assertRaisesMessage(CommandError, "конвейер"):
            pipe_commands(
                ["/bin/sh", "-c", "dd if=/dev/zero bs=1M count=8 2>/dev/null"],
                ["false"],
            )
