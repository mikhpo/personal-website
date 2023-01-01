import os
import unittest
from pathlib import Path

class StorageTest(unittest.TestCase):
    '''Тестирование доступности системы хранения.'''

    def test_storage_dir_exists(self):
        '''Проверить, что директория для хранения медиафайлов существует.'''
        development_dir = Path(__file__).resolve().parent.parent.parent.parent
        storages_dir = os.path.join(development_dir, 'Storages')
        media_dir = os.path.join(storages_dir, 'personal_website')
        self.assertTrue(os.path.exists(media_dir))

if __name__ == '__main__':
    unittest.main()