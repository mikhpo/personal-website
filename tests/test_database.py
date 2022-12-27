import os
import unittest
import psycopg2
from dotenv import load_dotenv

def connect_postgres(dbname: str, user: str, host: str, port: str, password: str):
    '''Подключиться к базе данных PostgreSQL.'''
    conn = psycopg2.connect(f'dbname={dbname} user={user} host={host} port={port} password={password} connect_timeout=1')
    return conn

def postgres_connected(dbname: str, user: str, host: str, port: str, password: str):
    '''Подключиться к базе данных PostgreSQL и вернуть булево значение в зависимости от успешности подключения.'''
    try:
        conn: psycopg2.connection = connect_postgres(dbname, user, host, port, password)
        conn.close()
        return True
    except:
        return False

def postgres_migrated(dbname: str, user: str, host: str, port: str, password: str):
    '''
    Подключиться к базе данных PostgreSQL и получить данные из таблицы миграций. 
    Вернуть булево значение в зависимости от успешности запроса.
    '''
    try:
        conn: psycopg2.connection = connect_postgres(dbname, user, host, port, password)
        cur = conn.cursor()
        cur.execute("SELECT * FROM django_migrations;")
        cur.fetchall()
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
        cls.dbname = os.environ['PG_NAME']
        cls.user = os.environ['PG_USER']
        cls.host = os.environ['PG_HOST']
        cls.port = os.environ['PG_PORT']
        cls.password = os.environ['PG_PASSWORD']
    
    def test_postgres_connection(self):
        '''Проверить подключение к основной базе данных PostgreSQL.'''
        self.assertTrue(postgres_connected(self.dbname, self.user, self.host, self.port, self.password))

    def test_postgres_migrated(self):
        '''Проверить наличие таблицы с миграциями в базе данных PostgreSQL'''
        self.assertTrue(postgres_migrated(self.dbname, self.user, self.host, self.port, self.password))

if __name__ == '__main__':
    unittest.main()