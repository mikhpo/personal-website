import os
import unittest
from pathlib import Path
from dotenv import load_dotenv

class SecretsTest(unittest.TestCase):
    '''Проверка на то, что секреты загружаются.'''

    environment_variables = (
        'DEBUG',
        'SECRET_KEY',
        'PG_NAME',
        'PG_USER',
        'PG_PASSWORD',
        'PG_HOST',
        'PG_PORT',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD'
    )

    def test_dotenv_path(self):
        '''Проверка на наличие в коревной директории проекта файла .env с переменными окружения.'''
        base_path = Path(__file__).parent.parent
        dotenv_filepath = os.path.join(base_path, '.env')
        self.assertTrue(os.path.exists(dotenv_filepath))

    def test_dotenv_load(self):
        '''Проверка на корректность загрузки переменных окружения из .env файла.'''
        self.assertTrue(load_dotenv())
        for variable in self.environment_variables:
            self.assertIsNotNone(os.environ[variable])

if __name__ == '__main__':
    unittest.main()