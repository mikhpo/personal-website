'''Скрипт для создания резервной копии базы данных PostgreSQL и сохранения на локальном диске.'''
import os
import shlex
import shutil
import locale
import subprocess
from pathlib import Path
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from apps.scripts.utils import get_folder_size

class Command(BaseCommand):
    help = 'Создание дампа базы данных PostgreSQL'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write("Запущен скрипт для создания дампа базы данных")

            # Параметры базы данных считываются из секретов, получение которых определено в модуле settings.
            get_secret = settings.GET_SECRET # функция для получения секретов

            # Сначала создадим дамп базы данных. Для этого используем вызов bash скрипта, использующего команду pg_dump.
            dump_dir = f'/home/{settings.SERVER_USER}/backups/' # директория, куда сохраняется дамп
            Path(dump_dir).mkdir(parents=True, exist_ok=True) # убедимся, что директория создана
            dump_name = f'pw_db_dump_{datetime.today().date()}' # имя дампа
            dump_path = os.path.join(dump_dir, dump_name) # полный путь до файла дампа

            # Если файл дампа сегодня уже был создан, то необходимо его удалить.
            if Path(dump_path).exists():
                self.stdout.write(f"Сегодня уже был создан дамп {dump_path}. Ранее созданный дамп будет удален")
                shutil.rmtree(dump_path)

            # Вызовем bash скрипт для создания дампа базы данных. Аргументы для скрипта считываются из модуля settings.
            bash_script = f'pg_dump "host={get_secret("DB_ID_PROD")} port={get_secret("DB_PORT_PROD")} sslmode=verify-full dbname={get_secret("DB_NAME_PROD")} user={get_secret("DB_USER")}" --no-privileges --no-subscriptions --no-publications -Fd -f {dump_path}'
            self.stdout.write(f"Выполняю команду: {bash_script}")

            # Bash-команда из строки токенизируется в список аргументов.
            arguments = shlex.split(bash_script) 
            
            # Пароль от базы данных PostgreSQL передается в качестве переменной окружения.
            process = subprocess.Popen(
                arguments,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                env = {'PGPASSWORD': get_secret("DB_PASSWORD")}
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
                
            # Если выполнение скрипта успешно завершено, то направим в stdout 
            # строку с результатом и указанием адресов получателей бэкапа.
            if Path(dump_path).exists():
                size = get_folder_size(dump_path, "КБ")
                self.stdout.write(self.style.SUCCESS(f"Дамп базы данных PostgreSQL сохранен по адресу {dump_path}. Размер дампа: {size}"))
                return dump_path
            else:
                raise CommandError('Дамп базы данных PostgreSQL не был сохранен')
        except Exception as error:
            raise CommandError(error)