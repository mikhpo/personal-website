'''
Перенос базы данных из продуктивной среды в среду разработки. Выполняется в два этапа:
1. Вызов комнады на создание дампа базы данных.
2. Восстановление базы данных из дампа.
'''
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Перенос базы данных PostgreSQL из продуктивной среды в среду разработки'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write('Запущен скрипт для переноса базы данных из продуктивной среды')
            dump = call_command('dump_db') # создание дампа базы данных
            call_command('copy_db', dump) # восстановление базы данных из дампа
        except Exception as error:
            raise CommandError(error)