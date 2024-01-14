import os
import unittest

import psycopg
from dotenv import load_dotenv


class TestPostgres(unittest.TestCase):
    """
    Тесты базы данных PostgreSQL.
    """

    @classmethod
    def setUpClass(cls):
        """
        Определить параметры подключения.
        """
        super().setUpClass()
        load_dotenv()
        cls.host = os.environ["POSTGRES_HOST"]
        cls.port = os.environ["POSTGRES_PORT"]
        cls.user = os.environ["POSTGRES_USER"]
        cls.password = os.environ["POSTGRES_PASSWORD"]
        cls.dbname = os.environ["POSTGRES_NAME"]

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
        except psycopg.OperationalError:
            return False

    def test_postgres_connection(self):
        """
        Проверить подключение к основной базе данных PostgreSQL.
        """
        postgres_connected = self.postgres_connected()
        self.assertTrue(postgres_connected)


if __name__ == "__main__":
    unittest.main()
