import os

import psycopg
from django.test import SimpleTestCase
from dotenv import load_dotenv


class PostgresTests(SimpleTestCase):
    """
    Тесты базы данных PostgreSQL.
    """

    @classmethod
    def setUpClass(cls):
        """
        Прочитать настройки проекта Django.
        """
        super().setUpClass()
        load_dotenv()
        cls.dbname = os.environ["POSTGRES_NAME"]
        cls.user = os.environ["POSTGRES_USER"]
        cls.host = os.environ["POSTGRES_HOST"]
        cls.port = os.environ["POSTGRES_PORT"]
        cls.password = os.environ["POSTGRES_PASSWORD"]

    def connect_postgres(self):
        """
        Подключиться к базе данных PostgreSQL.
        """
        conn = psycopg.connect(
            f"dbname={self.dbname} user={self.user} host={self.host} port={self.port} password={self.password} connect_timeout=1"
        )
        return conn

    def postgres_connected(self):
        """
        Подключиться к базе данных PostgreSQL и вернуть булево значение в зависимости от успешности подключения.
        """
        try:
            conn = self.connect_postgres()
            conn.close()
            return True
        except:
            return False

    def test_postgres_connection(self):
        """
        Проверить подключение к основной базе данных PostgreSQL.
        """
        postgres_connected = self.postgres_connected()
        self.assertTrue(postgres_connected)
