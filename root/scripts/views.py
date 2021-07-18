import os
import subprocess
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.utils.timezone import now
from .models import Script, Run
from loguru import logger


@logger.catch
def database_dump(request):
    '''Функция создает дамп базы данных сайта и отправляет по электронной почте.'''
    log = [] # создаем пустой список, куда будем поэтапно записывать журнал
    # Журнал выполнения скриптов будем записывать в лог-файл, который ротируется еженедельно.
    logger.add("scripts/logs/database_dump.log", rotation="12:00") 

    # Создадим объект запущенного скрипта.
    run = Run.objects.create(
        status = 0
        )
    run.save()
    
    try:
        url = request.build_absolute_uri() # определяем путь
        text = f'Поступил запрос: {url}'
        log.append(text)
        logger.debug(text)

        script = Script.objects.get(command = url) # найдем скрипт по пути
        run.script = script
        run.save()
        text = f'Запускаю скрипт: {script.name}'
        log.append(text)
        logger.debug(text)
    
        # Сначала создадим дамп базы данных. Для этого используем вызов bash скрипта, использующего команду pg_dump.
        backup_dir = f'/home/{settings.SERVER_USER}/backups' # директория, куда сохраняется дамп
        dump_name = 'personal_website_backup.sql' # имя дампа
    
        # Вызовем bash скрипт для создания дампа базы данных.
        bash_script = f'PGPASSWORD="{settings.DATABASES["default"]["PASSWORD"]}" pg_dump -U {settings.DATABASES["default"]["USER"]} -h localhost {settings.DATABASES["default"]["NAME"]} > {dump_name}'
        text = f'Запускаю bash скрипт: {bash_script}'
        log.append(text)
        logger.debug(text)
        subprocess.call(
            bash_script, 
            shell=True, 
            cwd=backup_dir
        )
        dump_path = os.path.join(backup_dir, dump_name) # полный путь до файла дампа
        text = f'Bash скрипт выполнен. Полный путь до файла дампа: {dump_path}'
        log.append(text)
        logger.debug(text)
        
        # Отправим письмо администраторам сайта.
        text = 'Отправляю письмо администраторам сайта'
        log.append(text)
        logger.debug(text)
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
        text = f'Письмо отправлено на {", ".join(admin_emails)}'
        log.append(text)
        logger.debug(text)

        # Если выполнение скрипта успешно завершено, то направим ответ с указанием адресов получателей бэкапа.
        message = f"Бэкап базы данных создан и отправлен на {', '.join(admin_emails)}\n"
        run.success = True

    except Exception as e:
        # Если при выполнении скрипта получили ошибку, то результатом будет текст ошибки.
        message = e
        logger.exception(message)
        run.success = False

    run.status = 1
    run.end = now()
    run.result = message
    run.log = "\n".join(log)
    run.save()   

    return HttpResponse(message)