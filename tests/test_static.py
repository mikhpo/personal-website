import os
import unittest
from pathlib import Path

class StaticFilesTest(unittest.TestCase):
    '''Тестирование готовности статических файлов проекта Django.'''

    @classmethod
    def setUpClass(cls):
        cls.base_path = Path(__file__).parent.parent
        cls.static_dir = os.path.join(cls.base_path, 'personal_website', 'static')

    def test_static_files_dir_exists(self):
        '''Проверяет наличие папки со статическими файлами в нужном месте.'''
        self.assertTrue(os.path.exists(self.static_dir))

    def test_node_modules_dir_exists(self):
        '''Проверяет наличие папки с модулями npm в нужном месте.'''
        node_modules_dir = os.path.join(self.base_path, 'node_modules')
        self.assertTrue(os.path.exists(node_modules_dir))

    def test_static_files_collected(self):
        '''Проверяет, что выполнена административная команда collectstatic.'''
        admin_staticfiles_dir = os.path.join(self.static_dir, 'admin')
        self.assertTrue(os.path.exists(admin_staticfiles_dir))

    def test_node_modules_symlink_created(self):
        '''Проверяет, что создана символическая ссылка на пакет модулей npm в директории статических файлов.'''
        symlink_path = os.path.join(self.static_dir, 'node_modules')
        self.assertTrue(os.path.islink(symlink_path))

if __name__ == '__main__':
    unittest.main()