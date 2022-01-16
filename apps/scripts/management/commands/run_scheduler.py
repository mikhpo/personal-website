'''
Команда на запуск планировщика скриптов. 
Планировщик скриптов считывает из базы данных
параметры запуска скриптов:
- Слаги (названия команд).
- Крон-выражения.
'''
import os
import warnings
from pytz_deprecation_shim import PytzUsageWarning
from loguru import logger
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.scripts.models import Job
from apps.scripts.tools import run_command

class Command(BaseCommand):
    help = 'Запуск планировщика скриптов'

    # Игнорирование предупреждений модуля pytz.
    warnings.filterwarnings("ignore", category=PytzUsageWarning)

    # Определение параметров логирования планировщика скриптов.
    logger.add(
        os.path.join(settings.BASE_DIR, 'logs', 'scheduler.log'),
        retention='1 month',
        backtrace=False,
        diagnose=True,
        format="{time:DD-MM-YYYY HH:mm:ss} | {level} | {message}"           
    )

    @logger.catch
    def handle(self, *args, **kwargs):
        '''Основная функция скрипта.'''
        # Планировщик скриптов будет единственной задачей, выполняемой в этом процессе.
        scheduler = BlockingScheduler()

        # Получение списка скриптов для добавления в планировщик. 
        # Параметры скриптов считываются из базы данных.
        jobs = Job.objects.filter(active=True, scheduled=True, cron__isnull=False)
        
        # Каждый из отобранных из базы данных скриптов добавляется в планировщик.
        for job in jobs:
            trigger = CronTrigger.from_crontab(job.cron)
            scheduler.add_job(
                run_command, 
                args=(job.slug,), 
                trigger=trigger,
                id=job.slug
            )
            logger.info(f'В планировщик скриптов добавлена задача {job.slug} с расписанием {job.cron}.')

        # Непосредственно запуск планировщика.
        try:
            logger.info('Планировщик скриптов запущен.')
            scheduler.start()
        except KeyboardInterrupt:
            logger.info('Выполнение планировщика скриптов прервано вручную.')
        except Exception as error:
            logger.exception(f'Ошибка запуска планировщика скриптов: {str(error)}.')