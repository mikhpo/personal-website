"""Команда резервного копирования только медиа."""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from backup.services import backup_media


class Command(BaseCommand):
    """Зеркальная синхронизация медиа в настроенные цели."""

    help = "Резервное копирование медиа в настроенные цели"

    def add_arguments(self, parser: CommandParser) -> None:
        """Добавить флаг проверки целей."""
        parser.add_argument("--verify", action="store_true", help="проверить цели, не создавая новый бэкап")

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ANN401, ARG002
        """Выполнить бэкап медиа либо проверку их целей."""
        backup_media(verify=options["verify"])
