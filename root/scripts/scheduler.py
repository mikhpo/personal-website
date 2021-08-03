
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from .models import Job
from .management.commands._tools import run_command
from django.conf import settings

scheduler = BackgroundScheduler()

def start():
    '''
    Функция для запуска планировщика скриптов.
    Выгружает из базы данных список скриптов, для которых установлены крон-выражение и флаги для автоматического запуска.
    Таким образом, управление планировщиком осуществляется через изменение объектов в базе данных приложения.
    '''
    if settings.START_SCHEDULER:
        jobs = Job.objects.filter(active=True, scheduled=True, cron__isnull=False)
        for job in jobs:
            trigger = CronTrigger.from_crontab(job.cron)
            scheduler.add_job(
                run_command, 
                args=(job.slug,), 
                trigger=trigger,
                id=job.slug
                )
        scheduler.start()
        logger.info("Планировщик скриптов запущен")
    else:
        logger.ingo("Планировщик скриптов не запущен")

