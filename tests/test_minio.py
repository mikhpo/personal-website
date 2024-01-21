import os
import re
import unittest
from http import HTTPStatus

import requests
from minio import Minio
from minio.error import S3Error


class TestMinio(unittest.TestCase):
    """Интеграционные тесты объектного хранилища MinIO."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.endpoint_url = os.getenv("MINIO_SERVER_URL")
        cls.console_url = os.getenv("MINIO_BROWSER_REDIRECT_URL")
        cls.access_key = os.getenv("MINIO_ACCESS_KEY")
        cls.secret_key = os.getenv("MINIO_SECRET_KEY")
        return super().setUpClass()

    def test_minio_healthcheck_ok(self):
        """Проверить доступность сервиса по специальному маршруту."""
        healthcheck_url = f"{self.endpoint_url}/minio/health/live"
        response = requests.get(healthcheck_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_console_response_ok(self):
        """Консоль сервиса доступен по заданному эндпоинту."""
        response = requests.get(self.console_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_python_sdk_connected(self):
        """
        Подключение через Python SDK проходит успешно.
        При создании клиента Minio необходимо указывать endpoint без протокола.
        """
        endpoint = re.sub(r"((http://)|(https://))", "", self.endpoint_url)
        client = Minio(endpoint, access_key=self.access_key, secret_key=self.secret_key, secure=False)
        check = self.check_bucket(client)
        self.assertTrue(check)

    def check_bucket(self, client: Minio):
        """Проверяет подключение получением доступа к бакету или созданием бакета."""
        try:
            bucket_name = "python-test-bucket"
            found = client.bucket_exists(bucket_name)
            if not found:
                client.make_bucket(bucket_name)
                client.remove_bucket(bucket_name)
                return True
            else:
                client.remove_bucket(bucket_name)
                return True
        except S3Error:
            return False


if __name__ == "__main__":
    unittest.main()
