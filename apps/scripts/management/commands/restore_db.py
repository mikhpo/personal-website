'''Скрипт для восстановления базы данных PostgreSQL из резервной копии.'''
import shlex
import locale
import subprocess
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from apps.scripts.utils import get_folder_size

class Command(BaseCommand):
    help = '''Восстановление базы данных PostgreSQL из дампа'''

    def add_arguments(self, parser):
        parser.add_argument('dump', nargs='?', type=str, help='Абсолютный путь к дампу базы данных')

    def handle(self, *args, **options):
        try:
            self.stdout.write("Запущен скрипт для восстановления базы данных из дампа") 

            # Адрес дампа передается скрипту в качестве аргумента командной строки. 
            dump = options['dump']
            size = get_folder_size(dump, "КБ")
            self.stdout.write(f"Адрес дампа: {dump}. Размер дампа: {size}")

            # Параметры базы данных по умолчанию из конфигурационного модуля Django.
            database = settings.DATABASES["default"]

            # Вызовем bash скрипт для восстановления базы данных из дампа при помощи утилиты pg_restore. 
            # Аргументы для скрипта считываются из модуля settings.
            bash_script = f'pg_restore -Fd --single-transaction --clean -h {database["HOST"]} -U {database["USER"]} -p {database["PORT"]} -d {database["NAME"]} {dump}'
            self.stdout.write(f"Выполняю команду: {bash_script}")

            # Синхронный вызов bash-скрипта.
            arguments = shlex.split(bash_script)
            process = subprocess.Popen(
                arguments,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                env = {'PGPASSWORD': database['PASSWORD']}
            )

            # Ожидаем результата выполнения bash-команды. 
            stdout, stderr = process.communicate()

            # Определение кодировки по умолчанию.
            encoding = locale.getdefaultlocale()[1]

            # Стандартный вывод и стандартная ошибка являются байтами, 
            # которые необходимо преобразовать в строку для лучшего форматирования.
            if stderr:
                raise CommandError(stderr.decode(encoding=encoding))
            elif len(stdout)>0:
                self.stdout.write(stderr.decode(encoding=encoding))
            else:
                self.stdout.write("Выполнение команды завершено")

            # Если выполнение скрипта успешно завершено, то направим в stdout сообщение о результате.
            self.stdout.write(self.style.SUCCESS("База данных PostgreSQL восстановлена из дампа"))
        except Exception as error:
            raise CommandError(error)