"""Тесты S3-сервера локального стека."""

import os
import unittest
import uuid

import boto3
import requests
from botocore.client import BaseClient, Config

ENDPOINT = os.getenv("AWS_S3_ENDPOINT_URL")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def _s3_client() -> BaseClient:
    """Клиент boto3 к S3-серверу из переменных окружения."""
    return boto3.client(
        "s3",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        endpoint_url=ENDPOINT,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def _server_available() -> bool:
    """Сервер S3 доступен и принимает ключи из окружения."""
    if not (ENDPOINT and ACCESS_KEY and SECRET_KEY):
        return False
    try:
        _s3_client().list_buckets()
    except Exception:  # noqa: BLE001
        return False
    return True


S3_SERVER_AVAILABLE = _server_available()


@unittest.skipUnless(S3_SERVER_AVAILABLE, "S3-сервер недоступен")
class TestS3Server(unittest.TestCase):
    """Живость эндпоинта и SDK-доступ локального S3-сервера."""

    def test_endpoint_responds(self) -> None:
        """Корень эндпоинта отвечает по HTTP (семантика healthcheck compose)."""
        assert ENDPOINT is not None
        response = requests.get(ENDPOINT, timeout=10)
        self.assertLess(response.status_code, 500)

    def test_boto3_bucket_round_trip(self) -> None:
        """boto3 работает с сервером: тестовый бакет создается, листируется и удаляется."""
        client = _s3_client()
        bucket = f"python-test-{uuid.uuid4().hex[:8]}"
        client.create_bucket(Bucket=bucket)
        try:
            names = [item["Name"] for item in client.list_buckets()["Buckets"]]
            self.assertIn(bucket, names)
        finally:
            client.delete_bucket(Bucket=bucket)
        names = [item["Name"] for item in client.list_buckets()["Buckets"]]
        self.assertNotIn(bucket, names)
