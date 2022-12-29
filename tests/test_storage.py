import os
import unittest
from minio import Minio
from dotenv import load_dotenv

def minio_connected(client: Minio):
    '''Попытаться создать подключение к Minio и вернуть булево значение в зависимости от результата.'''
    try:
        client.list_buckets()
        return True
    except:
        return False

class MinioTest(unittest.TestCase):
    '''Тестирование подключения и конфигурации Minio S3.'''

    @classmethod
    def setUpClass(cls):
        '''Подключиться к серверу Minio.'''
        load_dotenv()
        cls.client = Minio(
            os.environ['MINIO_ENDPOINT'], 
            access_key=os.environ['MINIO_ACCESS_KEY'], 
            secret_key=os.environ['MINIO_SECRET_KEY'], 
            secure=False
        )
        cls.bucket = os.environ['MINIO_MEDIA_FILES_BUCKET']

    def test_minio_connection(self):
        '''Проверить, что подключение к Minio создается.'''
        self.assertTrue(minio_connected(self.client))
    
    def test_project_bucket_exists(self):
        '''Проверить, что бакет проекта существует.'''
        self.assertTrue(self.client.bucket_exists(self.bucket))

if __name__ == '__main__':
    unittest.main()