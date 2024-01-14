import os
from importlib.util import find_spec

from django.conf import settings
from django.test import SimpleTestCase

REQUIRED_PACKAGES = ("django", "gunicorn", "psycopg", "whitenoise", "PIL")


class PythonPackagesTests(SimpleTestCase):
    """
    Проверка на то, что сторонние пакеты установлены.
    """

    def test_python_venv_present(self):
        """
        Проверка на то, что папка виртуального окружения создана в корневой директории проекта.
        """
        venv_path = os.path.join(settings.PROJECT_DIR, ".venv")
        self.assertTrue(os.path.exists(venv_path))

    def test_python_packages_installed(self):
        """
        Проверяет, что все пакеты Python установлены.
        """
        for package in REQUIRED_PACKAGES:
            spec = find_spec(package)
            self.assertIsNotNone(spec)
