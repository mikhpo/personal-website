import os
import unittest
import pkg_resources
from pathlib import Path
from dotenv import load_dotenv

class PackagesTest(unittest.TestCase):
    '''Проверка на то, что сторонние пакеты установлены.'''

    python_packages = [
        'django',
        'gunicorn',
        'psycopg2-binary',
        'whitenoise',
        'pillow',
        'django-crispy-forms',
        'django-tinymce',
        'django-environ',
        'python-dotenv',
        'pytils',
    ]

    def test_python_venv_present(self):
        '''Проверка на то, что папка виртуального окружения создана в корневой директории проекта.'''
        base_path = Path(__file__).parent.parent
        venv_path = os.path.join(base_path, '.venv')
        self.assertTrue(os.path.exists(venv_path))
        
    def test_python_packages_installed(self):
        '''Проверяет, что все пакеты Python установлены.'''
        working_set = pkg_resources.working_set
        installed_packages_list = sorted([f'{package.key}=={package.version}' for package in working_set])
        installed_packages = ', '.join(installed_packages_list)
        for package in self.python_packages:
            self.assertIn(package, installed_packages)

class SecretsTest(unittest.TestCase):
    '''Проверка на то, что секреты загружаются.'''

    environment_variables = [
        'DEBUG',
        'SECRET_KEY',
        'PG_NAME',
        'PG_USER',
        'PG_PASSWORD',
        'PG_HOST',
        'PG_PORT',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
    ]

    def test_dotenv_path(self):
        '''Проверка на наличие в коревной директории проекта файла .env с переменными окружения.'''
        base_path = Path(__file__).parent.parent
        dotenv_filepath = os.path.join(base_path, '.env')
        self.assertTrue(os.path.exists(dotenv_filepath))

    def test_dotenv_load(self):
        '''Проверка на корректность загрузки переменных окружения из .env файла.'''

        # Проверяется, что переменные не заданы на глобальном уровне.
        with self.assertRaises(KeyError):
            for variable in self.environment_variables:
                os.environ[variable]

        # Проверяется, что все нужные переменные загружены из .env файла.
        self.assertTrue(load_dotenv())
        for variable in self.environment_variables:
            self.assertIsNotNone(os.environ[variable])

if __name__ == '__main__':
    unittest.main()