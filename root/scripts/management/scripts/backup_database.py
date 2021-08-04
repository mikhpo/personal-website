import os
import time
import subprocess
from loguru import logger
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from pathlib import Path
from .tools import format_time

def main():
    '''Функция создает дамп базы данных сайта и отправляет по электронной почте.'''

    # Фиксируем точку отсчета времени выполнения скрипта.
    start_time = time.time()
    
    # Сначала создадим дамп базы данных. Для этого используем вызов bash скрипта, использующего команду pg_dump.
    backup_dir = f'/home/{settings.SERVER_USER}/backups' # директория, куда сохраняется дамп
    Path(backup_dir).mkdir(parents=True, exist_ok=True) # убедимся, что директория создана
    dump_name = 'personal_website_backup.sql' # имя дампа

    # Вызовем bash скрипт для создания дампа базы данных.
    bash_script = f'PGPASSWORD="{settings.DATABASES["default"]["PASSWORD"]}" pg_dump -U {settings.DATABASES["default"]["USER"]} -h localhost {settings.DATABASES["default"]["NAME"]} > {dump_name}'
    logger.debug(f'Запускаю bash скрипт: {bash_script}')
    subprocess.call(
        bash_script, 
        shell=True, 
        cwd=backup_dir
    )
    dump_path = os.path.join(backup_dir, dump_name) # полный путь до файла дампа
    logger.debug(f'Bash скрипт выполнен. Полный путь до файла дампа: {dump_path}')
    
    # Отправим письмо администраторам сайта.
    logger.debug('Отправляю письмо администраторам сайта')
    admin_users = User.objects.filter(is_staff=True)
    admin_emails = []
    for user in admin_users:
        admin_emails.append(user.email)

    email = EmailMessage(
        'Бэкап базы данных персонального сайта',
        'Автоматический бэкап базы данных персонального сайта.\nВо вложении дамп базы данных PostgreSQL.',
        settings.DEFAULT_FROM_EMAIL,
        admin_emails,
    )
    email.attach_file(dump_path)
    email.send()
    logger.debug(f'Письмо отправлено на {", ".join(admin_emails)}')

    # Определяем продолжительность выполнения скрипта
    overall_time = time.time() - start_time

    # Если выполнение скрипта успешно завершено, то направим ответ с указанием адресов получателей бэкапа.
    result = f"Бэкап базы данных создан и отправлен на {', '.join(admin_emails)} за {format_time(overall_time)} минут."
    return result