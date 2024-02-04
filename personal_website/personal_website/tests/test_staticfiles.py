"""Тесты статических файлов."""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class StaticFilesTests(SimpleTestCase):
    """Тестирование готовности статических файлов проекта Django."""

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D102
        super().setUpClass()
        cls.static_dir = Path(settings.PROJECT_DIR) / "static"

    def test_static_files_dir_exists(self) -> None:
        """Проверяет наличие папки со статическими файлами в нужном месте."""
        dir_exists = Path(self.static_dir).exists()
        self.assertTrue(dir_exists)

    def test_node_modules_dir_exists(self) -> None:
        """Проверяет наличие папки с модулями npm в нужном месте."""
        node_modules_dir = Path(settings.PROJECT_DIR) / "node_modules"
        dir_exists = Path(node_modules_dir).exists()
        self.assertTrue(dir_exists)

    def test_static_files_collected(self) -> None:
        """Проверяет, что выполнена административная команда collectstatic."""
        admin_staticfiles_dir = self.static_dir / "admin"
        dir_exists = Path(admin_staticfiles_dir).exists()
        self.assertTrue(dir_exists)
