"""Команда восстановления медиа из цели."""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from backup.services import restore_media


class Command(BaseCommand):
    """Восстановление медиа из storage/ указанной цели."""

    help = "Восстановление медиа из storage/ цели"

    def add_arguments(self, parser: CommandParser) -> None:
        """Добавить аргумент имени цели."""
        parser.add_argument("target", help="имя цели, из которой восстанавливается медиа")

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ANN401, ARG002
        """Восстановить медиа из указанной цели."""
        restore_media(options["target"])
