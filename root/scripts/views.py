from django.http import HttpResponse
import subprocess
from django.conf import settings
import os
from django.core.mail import EmailMessage
from django.contrib.auth.models import User

# Create your views here.

def database_dump(request):
    '''Функция создает дамп базы данных сайта и отправляет по электронной почте.'''

    # Сначала создадим дамп базы данных. Для этого используем вызов bash скрипта, использующего команду pg_dump.
    backup_dir = '/home/mikhpo/backups' # директория, куда сохраняется дамп
    dump_name = 'personal_website_backup.sql' # имя дампа

    # Вызовем bash скрипт для создания дампа базы данных.
    subprocess.call(
        f'PGPASSWORD="{settings.DATABASES["default"]["PASSWORD"]}" pg_dump -U {settings.DATABASES["default"]["USER"]} -h localhost {settings.DATABASES["default"]["NAME"]} > {dump_name}', 
        shell=True, 
        cwd=backup_dir
    )
    dump_path = os.path.join(backup_dir, dump_name) # полный путь до файла дампа

    # Отправим письмо администраторам сайта.
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
    return HttpResponse(f"Бэкап базы данных создан и отправлен {', '.join(admin_emails)}")


