'''
Скрипт для создания бэкапа базы данных PostgreSQL 
и отправки администраторам по электронной почте.
'''
import os
import subprocess
from pathlib import Path
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from scripts.decorators import log_script

class Command(BaseCommand):
    help = '''Резервное копирование базы данных PostgreSQL'''

    @log_script
    def handle(self, *args, **kwargs):        
        # Сначала создадим дамп базы данных. Для этого используем вызов bash скрипта, использующего команду pg_dump.
        backup_dir = f'/home/{settings.SERVER_USER}/backups' # директория, куда сохраняется дамп
        Path(backup_dir).mkdir(parents=True, exist_ok=True) # убедимся, что директория создана
        dump_name = 'personal_website_backup.sql' # имя дампа
        dump_path = os.path.join(backup_dir, dump_name) # полный путь до файла дампа

        # Параметры базы данных по умолчанию из конфигурационного модуля Django.
        database = settings.DATABASES["default"]

        # Вызовем bash скрипт для создания дампа базы данных.
        # Аргументы для скрипта считываются из модуля settings.
        bash_script = f'PGPASSWORD="{database["PASSWORD"]}" pg_dump -U {database["USER"]} -h localhost {database["NAME"]} > {dump_path}'

        # Синхронный вызов bash-скрипта.
        subprocess.call(
            bash_script, 
            shell=True
        )
        
        # Определение администраторов сайта. Администраторы сайта - это пользователи с ролью суперпользователя.
        admin_users = User.objects.filter(is_superuser=True)
        admin_emails = []
        for user in admin_users:
            admin_emails.append(user.email)

        # Использование класса EmailMessage обусловлено необходимостью отправить письмо с вложением.
        email = EmailMessage(
            'Бэкап базы данных персонального сайта',
            '''
            Автоматический бэкап базы данных персонального сайта.\n
            Во вложении дамп базы данных PostgreSQL.
            ''',
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
        )
        email.attach_file(dump_path)
        email.send()

        # Если выполнение скрипта успешно завершено, то направим в stdout 
        # строку с результатом и указанием адресов получателей бэкапа.
        return f"Бэкап базы данных создан и отправлен на {', '.join(admin_emails)}."