"""Тесты установленных пакетов Python."""
from importlib.util import find_spec
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class PythonPackagesTests(SimpleTestCase):
    """Проверка на то, что сторонние пакеты установлены."""

    required_packages = ("django", "gunicorn", "psycopg", "whitenoise", "PIL")

    def test_python_venv_present(self) -> None:
        """Проверка на то, что папка виртуального окружения создана в корневой директории проекта."""
        venv_path = Path(settings.PROJECT_DIR) / ".venv"
        path_exists = venv_path.exists()
        self.assertTrue(path_exists)

    def test_python_packages_installed(self) -> None:
        """Проверяет, что все пакеты Python установлены."""
        for package in self.required_packages:
            spec = find_spec(package)
            self.assertIsNotNone(spec)
