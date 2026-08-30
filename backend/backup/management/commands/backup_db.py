"""Команда резервного копирования только БД."""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from backup.reports import run_with_report
from backup.services import backup_db


class Command(BaseCommand):
    """Резервное копирование БД в настроенные цели."""

    help = "Резервное копирование БД в настроенные цели"

    def add_arguments(self, parser: CommandParser) -> None:
        """Добавить флаг проверки целей."""
        parser.add_argument("--verify", action="store_true", help="проверить цели, не создавая новый бэкап")

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ANN401, ARG002
        """Выполнить бэкап БД либо проверку её целей."""

        def backup_database() -> dict[str, Any]:
            return {"db": backup_db()}

        if options["verify"]:
            backup_db(verify=True)
            return
        run_with_report("backup_db", "backup_db", backup_database)
