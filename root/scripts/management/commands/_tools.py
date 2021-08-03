import sys
import subprocess
from django.conf import settings
from django.utils import timezone
from scripts.models import Job, Execution
from scripts.management.scripts import backup_database
from loguru import logger

python = settings.PYTHON_PATH
manage = settings.MANAGE_PATH

script_dit = {
    "backup_database": backup_database.main
}

@logger.catch
def command_handler(script):
    '''
    Универсальный обработчик комманд.
    Записывает состояние выполнения скриптов в базу данных.
    '''
    command = sys.argv[1]
    job = Job.objects.get(slug = command)
    execution = Execution.objects.create(status=0, job=job)
    execution.save()

    try:
        logger.debug(str(execution))
        job.last_run = timezone.localtime(timezone.now())
        job.save()
        result = script_dit[script]()
        logger.info(result)
        execution.success = 1
    except Exception as e:
        result = f'Ошибка: {e}'
        logger.exception(result)
        execution.success = 0
    
    execution.status = 1
    execution.end = timezone.localtime(timezone.now())
    execution.result = result
    execution.save()

def run_command(command):
    '''
    Функция для запуска выполнения абстрактной команды.
    Запускает команду в отдельном процессе, исспользуя конткст Django.
    Не дожидается окончания выполнения команды.
    '''
    arguments = [python, manage, command]
    return subprocess.Popen(arguments)
