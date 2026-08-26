"""Команда восстановления базы данных из дампа."""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from backup.services import restore_db


class Command(BaseCommand):
    """Восстановление БД из локального файла дампа либо последнего дампа цели."""

    help = "Восстановление БД из файла дампа или последнего дампа цели"

    def add_arguments(self, parser: CommandParser) -> None:
        """Добавить источник дампа и опциональное имя конкретного дампа."""
        parser.add_argument("source", help="путь к файлу дампа или имя цели")
        parser.add_argument("--dump", default=None, help="имя конкретного дампа в цели")

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ANN401, ARG002
        """Восстановить БД из указанного источника."""
        restore_db(options["source"], options["dump"])
