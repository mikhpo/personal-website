import os

from django.conf import settings
from django.test import SimpleTestCase


class StaticFilesTests(SimpleTestCase):
    """
    Тестирование готовности статических файлов проекта Django.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.static_dir = os.path.join(settings.PROJECT_DIR, "static")

    def test_static_files_dir_exists(self):
        """
        Проверяет наличие папки со статическими файлами в нужном месте.
        """
        self.assertTrue(os.path.exists(self.static_dir))

    def test_node_modules_dir_exists(self):
        """
        Проверяет наличие папки с модулями npm в нужном месте.
        """
        node_modules_dir = os.path.join(settings.PROJECT_DIR, "node_modules")
        self.assertTrue(os.path.exists(node_modules_dir))

    def test_static_files_collected(self):
        """
        Проверяет, что выполнена административная команда collectstatic.
        """
        admin_staticfiles_dir = os.path.join(self.static_dir, "admin")
        self.assertTrue(os.path.exists(admin_staticfiles_dir))
