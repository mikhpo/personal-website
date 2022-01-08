'''Переиспользуемые функции планировщика скриптов.'''
import subprocess
from django.conf import settings

python = settings.PYTHON_PATH
manage = settings.MANAGE_PATH

def run_command(command):
    '''
    Функция для запуска выполнения абстрактной команды.
    Запускает команду в отдельном процессе, исспользуя конткст Django.
    Не дожидается окончания выполнения команды.
    '''
    arguments = [python, manage, command]
    return subprocess.Popen(arguments)
