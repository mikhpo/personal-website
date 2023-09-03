import os

import pkg_resources
from django.conf import settings
from django.test import SimpleTestCase

PYTHON_PACKAGES = ("django", "gunicorn", "psycopg", "whitenoise", "boto3", "pillow")


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
        working_set = pkg_resources.working_set
        installed_packages_list = sorted(
            [f"{package.key}=={package.version}" for package in working_set]
        )
        installed_packages = ", ".join(installed_packages_list)
        for package in PYTHON_PACKAGES:
            self.assertIn(package, installed_packages)
