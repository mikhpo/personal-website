import os
import unittest
import pkg_resources
from pathlib import Path

class PackagesTest(unittest.TestCase):
    '''Проверка на то, что сторонние пакеты установлены.'''

    python_packages = (
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
        'django-minio-backend',
    )

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

if __name__ == '__main__':
    unittest.main()