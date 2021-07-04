import os
import subprocess
import traceback
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from .models import Script, Run

# Create your views here.

def database_dump(request):
    '''Функция создает дамп базы данных сайта и отправляет по электронной почте.'''
    url = request.build_absolute_uri()
    script = Script.objects.get(command = url)
    run = Run.objects.create(
        script = script,
        status = 0
        )
    run.save()
    
    try:
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

        # Если выполнение скрипта успешно завершено, то направим ответ с указанием адресов получателей бэкапа.
        message = f"Бэкап базы данных создан и отправлен на {', '.join(admin_emails)}\n"

    except Exception as e:
        # Если при выполнении скрипта получили ошибку, то направив ответ с трэйсбэком.
        message = traceback.print_exc()

    run.status = 1
    run.result = message
    run.save()   

    return HttpResponse(message)