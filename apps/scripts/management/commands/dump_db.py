'''Скрипт для создания резервной копии базы данных PostgreSQL и сохранения на локальном диске.'''
import os
from datetime import datetime
import subprocess, shlex
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

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

            # Вызовем bash скрипт для создания дампа базы данных. Аргументы для скрипта считываются из модуля settings.
            bash_script = f'pg_dump "host={get_secret("DB_ID_PROD")} port={get_secret("DB_PORT_PROD")} sslmode=verify-full dbname={get_secret("DB_NAME_PROD")} user={get_secret("DB_USER")}" -Fd -f {dump_path}'
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
            
            # Стандартный вывод и стандартная ошибка являются байтами, 
            # которые необходимо преобразовать в строку для лучшего форматирования.
            if stderr:
                raise CommandError(stderr.decode(encoding='UTF-8'))
            else:
                self.stdout.write(stdout.decode(encoding='UTF-8'))

            # Если выполнение скрипта успешно завершено, то направим в stdout 
            # строку с результатом и указанием адресов получателей бэкапа.
            self.stdout.write(self.style.SUCCESS(f"Дамп базы данных PostgreSQL сохранен по адресу {dump_path}"))
            return dump_path
        except Exception as error:
            raise CommandError(error)