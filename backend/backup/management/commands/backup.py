"""Команда полного резервного копирования БД и медиа."""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from backup.services import backup_db, backup_media


class Command(BaseCommand):
    """Резервное копирование БД и медиа в настроенные цели."""

    help = "Резервное копирование БД и медиа в настроенные цели"

    def add_arguments(self, parser: CommandParser) -> None:
        """Добавить флаг проверки целей."""
        parser.add_argument("--verify", action="store_true", help="проверить цели, не создавая новый бэкап")

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ANN401, ARG002
        """Выполнить бэкап БД и медиа либо проверку их целей."""
        backup_db(verify=options["verify"])
        backup_media(verify=options["verify"])
