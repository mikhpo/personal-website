"""Команда инициализации S3-хранилища."""

from typing import Any

from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from personal_website.utils import init_s3_bucket


class Command(BaseCommand):
    """Инициализация нового S3-хранилища: бакет и политика публичной раздачи.

    Правило собственности: существующий бакет не изменяется, поэтому
    внешние провайдеры (прод) политик от приложения не получают.
    """

    help = "Создать бакет и применить политику публичной раздачи; существующий бакет не изменяется"

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ANN401, ARG002
        """Инициализировать хранилище при STORAGE_TYPE=s3."""
        if settings.STORAGE_TYPE != "s3":
            self.stdout.write("STORAGE_TYPE не s3 - инициализация пропущена")
            return
        try:
            status = init_s3_bucket()
        except ClientError as error:
            msg = f"инициализация S3-хранилища не выполнена: {error}"
            raise CommandError(msg) from error
        if status == "created":
            self.stdout.write("Бакет создан, политика публичной раздачи применена")
        else:
            self.stdout.write("Бакет существует - изменения не выполнялись")
