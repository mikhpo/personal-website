"""Интеграционное тестирование кластера PostgreSQL."""
import os
import unittest
from typing import Optional

import psycopg
from dotenv import load_dotenv


class TestPostgres(unittest.TestCase):
    """Интеграционные тесты базы данных PostgreSQL."""

    @classmethod
    def setUpClass(cls) -> None:
        """Определить параметры подключения."""
        load_dotenv()
        cls.host = "localhost"
        cls.port = os.environ["POSTGRES_PORT"]
        cls.user = os.environ["POSTGRES_USER"]
        cls.password = os.environ["POSTGRES_PASSWORD"]
        cls.dbname = os.environ["POSTGRES_DB"]
        return super().setUpClass()

    def connect_postgres(self) -> psycopg.Connection[psycopg.connection.TupleRow]:
        """Подключиться к базе данных PostgreSQL."""
        connifo = "dbname={} user={} host={} port={} password={} connect_timeout=1".format(
            self.dbname,
            self.user,
            self.host,
            self.port,
            self.password,
        )
        return psycopg.connect(connifo)

    def postgres_connected(self) -> Optional[bool]:
        """Подключиться к базе данных PostgreSQL и вернуть булево значение в зависимости от успешности подключения."""
        try:
            conn = self.connect_postgres()
            conn.close()
        except psycopg.OperationalError:
            return False
        else:
            return True

    def test_postgres_connection(self) -> None:
        """Проверить подключение к основной базе данных PostgreSQL."""
        postgres_connected = self.postgres_connected()
        self.assertTrue(postgres_connected)


if __name__ == "__main__":
    unittest.main()
