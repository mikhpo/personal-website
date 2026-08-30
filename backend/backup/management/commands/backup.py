"""Команда полного резервного копирования БД и медиа."""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from backup.reports import run_with_report
from backup.services import backup_db, backup_media


class Command(BaseCommand):
    """Резервное копирование БД и медиа в настроенные цели."""

    help = "Резервное копирование БД и медиа в настроенные цели"

    def add_arguments(self, parser: CommandParser) -> None:
        """Добавить флаг проверки целей."""
        parser.add_argument("--verify", action="store_true", help="проверить цели, не создавая новый бэкап")

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ANN401, ARG002
        """Выполнить бэкап БД и медиа либо проверку их целей."""
        if options["verify"]:
            backup_db(verify=True)
            backup_media(verify=True)
            return

        def backup_both() -> dict[str, Any]:
            return {"db": backup_db(), "media": backup_media()}

        run_with_report("backup", "backup (БД и медиа)", backup_both)
