#!/usr/bin/env python3
# 
# Скрипт для создания бэкапа хранилища персонального сайта: медиа и загруженных файлов.

import os
import sys
import shlex
import subprocess
import locale
import logging
import logging.handlers
from pathlib import Path
from distutils.util import strtobool
from dotenv import load_dotenv

def set_logger():
    '''
    Установка настроек логирования.
    '''
    # Определение пути сохранения логов.
    base_dir = Path(__file__).resolve().parent.parent
    script_name = Path(__file__).resolve().stem
    logs_dir = os.path.join(base_dir, 'logs', script_name)
    os.makedirs(logs_dir, exist_ok = True)
    log_path = os.path.join(logs_dir, f'{script_name}.log')

    # Настройки логирования.
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    formatter = logging.Formatter(
        fmt='[{asctime}] [{levelname}] [{filename} -> {funcName} -> {lineno}] {message}', 
        datefmt='%d.%m.%Y %H:%M:%S', 
        style='{'
    )
    timed_rotating_handler = logging.handlers.TimedRotatingFileHandler(log_path, when='midnight', backupCount=7)
    timed_rotating_handler.setFormatter(formatter)
    logger.addHandler(timed_rotating_handler)
    return logger

def get_storage_size(storage_path: str) -> str:
    '''
    Определение размера папки с автоматическим определением единцы измерения.
    '''
    units = ("Б", "КБ", "МБ", "ГБ", "ТБ")

    # Задается первоначальный размер.
    size = 0

    # Определение размера всех файлов в папке в байтах.
    for path, _, files in os.walk(storage_path):
        for file in files:
            filepath = os.path.join(path, file)
            size += os.path.getsize(filepath)
    
    # Определение единцы измерения размера дампа. Значение округляется до целого числа и возвращается в виде строки с указанием размерности.
    for unit in units:
        if size < 1024:
            value = int(size)
            return f'{value} {unit}'
        size /= 1024  

def get_base_dir(mount_path: str, debug: bool):
    '''
    Определение базовой директории хранения бэкапов. Зависит от следующих факторов: 
    - подключен ли внешний жесткий диск, 
    - под какой точкой монтирования, 
    - какой режим запуска приложения.
    '''
    # Проверить, что внешний диск для хранения бэкапов смонтирован.
    if os.path.ismount(mount_path) and not debug:
        # Если диск смонтирован, то бэкап будет записан на него.
        base_dir = mount_path
    else:
        # Иначе бэкап будет записан в папку на системном диске.
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
    return base_dir

def get_source_path():
    '''
    Получить адрес папки-источника.
    '''
    projects_dir = Path(__file__).resolve().parent.parent.parent.parent
    storages_dir = os.path.join(projects_dir, 'Storages')
    source_dir = os.path.join(storages_dir, PROJECT_NAME)
    source_dir += os.sep
    return source_dir

def get_destination_path(base_dir: str):
    '''
    Получить адрес папки-назначения.
    '''
    backup_dir = os.path.join(base_dir, 'Backups')
    backup_path = os.path.join(backup_dir, PROJECT_NAME, 'storage')
    Path(backup_path).mkdir(parents=True, exist_ok=True)
    return backup_path

def compose_command(source_path: str, destination_path: str):
    '''
    Составить текст команды rsync.
    '''
    rsync = os.popen(f'which rsync').read().strip()
    rsync_command = f'{rsync} -r {source_path} {destination_path}'
    return rsync_command

def run_rsync(rsync_command: str):
    '''
    Выполннить команду rsync для синхронизации содержимого каталогов. 
    Получить стандартный вывод или стандартную ошибку.
    '''
    process = subprocess.Popen(
        args = shlex.split(rsync_command),
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE
    )

    # Ожидаем результата выполнения bash-команды. 
    stdout, stderr = process.communicate()
    return stdout, stderr

def main():
    '''
    Основное тело скрипта.
    '''
    logger.info("Запущен скрипт для создания бэкапа загруженных файлов проекта")

    # Получение параметров из переменных окружения.
    logger.info('Считывание переменных окружения из файла .env в корневой директории проекта')
    load_dotenv()
    mount_path = os.environ['STORAGE_DRIVE_MOUNT']
    debug = bool(strtobool(os.environ['DEBUG']))

    # Определение системной кодировки.
    encoding = locale.getlocale()[1]

    # Определение путей копирования файлов.
    base_dir = get_base_dir(mount_path, debug)
    source_path = get_source_path()
    destination_path = get_destination_path(base_dir)
    logger.info(f'Адрес папки-источника: {source_path}')
    logger.info(f'Адрес папки-назначения: {destination_path}')
    
    # Определение размера копируемых файлов.
    storage_size = get_storage_size(source_path)
    logger.info(f'Общий размер хранилища: {storage_size}')

    # Выполнить команду rsync, подставив переменные, и получить ответ.
    rsync_command = compose_command(source_path, destination_path)
    logger.info(f'Выполнение команды: {rsync_command}')
    stdout, stderr = run_rsync(rsync_command)

    # Стандартный вывод и стандартная ошибка являются байтами, 
    # которые необходимо преобразовать в строку для лучшего форматирования.
    if stderr:
        sys.exit(stderr.decode(encoding=encoding))
    elif len(stdout)>0:
        logger.info(stdout.decode(encoding=encoding))
    else:
        logger.info("Выполнение команды завершено")

if __name__ == '__main__':
    PROJECT_NAME = 'personal_website'
    logger = set_logger()
    try:
        main()
    except BaseException as e:
        logger.exception(e)
