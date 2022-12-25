import os
import unittest
from dotenv import load_dotenv
import psycopg2

def postgres_connected(dbname: str, user: str, host: str, port: str, password: str):
    '''Подключиться к базе данных PostgreSQL и вернуть булево значение в зависимости от успешности подключения.'''
    try:
        conn = psycopg2.connect(f'dbname={dbname} user={user} host={host} port={port} password={password} connect_timeout=1')
        conn.close()
        return True
    except:
        return False

class DatabaseTest(unittest.TestCase):
    '''Тесты базы данных.'''

    @classmethod
    def setUpClass(cls):
        '''Прочитать настройки проекта Django.'''
        load_dotenv()
    
    def test_postgres_connection(self):
        '''Проверить подключение к основной базе данных PostgreSQL.'''
        dbname = os.environ['PG_NAME']
        user = os.environ['PG_USER']
        host = os.environ['PG_HOST']
        port = os.environ['PG_PORT']
        password = os.environ['PG_PASSWORD']
        self.assertTrue(postgres_connected(dbname, user, host, port, password))

if __name__ == '__main__':
    unittest.main()