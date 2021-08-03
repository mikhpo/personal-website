from django.core.management.base import BaseCommand
from ._tools import command_handler

class Command(BaseCommand):
    help = '''Резервное копирование базы данных.'''

    def handle(self, *args, **options):
        command_handler('backup_database')


