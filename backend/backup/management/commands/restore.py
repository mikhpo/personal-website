"""Команда восстановления из целей резервного копирования."""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from backup.services import restore_db, restore_media


class Command(BaseCommand):
    """Восстановление базы данных или медиа из цели бэкапирования."""

    help = "Восстановление базы данных или медиа из цели бэкапирования"

    def add_arguments(self, parser: CommandParser) -> None:
        """Добавить аргументы вида восстановления и адреса цели."""
        parser.add_argument("kind", choices=["db", "media"], help="что восстанавливать: db или media")
        parser.add_argument("target", help="адрес цели; для db - также путь к файлу дампа")
        parser.add_argument("--dump", help="имя конкретного дампа в db/ цели (по умолчанию последний)")

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ANN401, ARG002
        """Восстановить выбранный источник из указанной цели."""
        if options["kind"] == "db":
            restore_db(options["target"], dump_name=options["dump"])
        else:
            restore_media(options["target"])
