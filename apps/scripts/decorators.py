'''Декоратор планировщика скриптов.'''
import os
import sys
from loguru import logger
from django.utils import timezone
from django.conf import settings
from apps.scripts.models import Job, Execution

def log_script(func):
    '''
    Декоратор для логирования результатов выполнения скриптов.
    Записывает состояние выполнения скриптов в базу данных.
    '''
    def handle(*args, **kwargs):
        # Определим наименование запускаемой команды.
        script = sys.argv[-1] # последний аргумент = наименование команды

        # Добавление лог-файла и определение параметров логирования. 
        # Название лог-файла = название команды.
        logger.add(
            os.path.join(
                settings.BASE_DIR,
                'logs', 'scripts',
                f'{script}.log'
            ),
            rotation="1 month",
            backtrace=False,
            diagnose=True,
            format="{time:DD-MM-YYYY HH:mm:ss} | {level} | {message}" 
        )

        # Определим в базе данных объект скрипта, выполнение которого инициировано.
        job = Job.objects.get(slug=script) # наименование команды = слаг скрипта в базе данных
        
        # Сохраним в базе данных объект, соответствующий отдельному выполнению скрипта.
        # Статус объекта = выполнение скрипта начато.
        execution = Execution.objects.create(status=0, job=job)
        execution.save()

        # Пустой список нужен для хранения частей результата выполнения.
        results = []

        try:
            # Пробуем выполнить скрипт. Если скрипт выполнен успешно,
            # то в качестве результата будет сохранена строка, возвращаемая скриптом.
            start_time = timezone.localtime(timezone.now())
            job.last_run = start_time
            job.save()
            output = func(*args, **kwargs)
            if not output:
                # Если скрипт не возвратил результат, то необходимо выдать исключение.
                raise Exception('cкрипт не возратил результат')
            else:
                execution.success = 1
        except Exception as error:
            # Если получаем исключение при выполнении скрипта, то в качестве
            # результата выполнения будет сохранен текст исключения.
            output = f'Ошибка: {str(error)}.'
            logger.exception(output)
            execution.success = 0
        finally:
            # В базу данных записывается результат со временем выполнения.
            results.append(output)
            execution.status = 1
            end_time = timezone.localtime(timezone.now())
            execution.end = end_time
            # Вычислим общее время выполнения скрипта.
            total_time = end_time - start_time
            total_time = "{:.2f}".format(total_time.total_seconds())
            results.append(f"Общее время выполнения скрипта: {total_time} сек.")
            result = " ".join(results)
            execution.result = result
            execution.save()
            logger.info(result)

    return handle
