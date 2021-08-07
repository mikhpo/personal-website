
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from .management.commands._tools import run_command
from django.conf import settings

scheduler = BackgroundScheduler()

def reschedule_job(slug, cron):
    '''Изменяет расписание уже созданной задачи APScheduler.'''
    trigger = CronTrigger.from_crontab(cron)
    scheduler.reschedule_job(job_id=slug, trigger=trigger)

def add_job(slug, cron):
    '''Добавляет в планировщик APScheduler новую задачу.'''
    trigger = CronTrigger.from_crontab(cron)
    scheduler.add_job(
                run_command, 
                args=(slug,), 
                trigger=trigger,
                id=slug
                )

def start():
    '''
    Функция для запуска планировщика скриптов.
    Выгружает из базы данных список скриптов, для которых установлены крон-выражение и флаги для автоматического запуска.
    Таким образом, управление планировщиком осуществляется через изменение объектов в базе данных приложения.
    '''
    from .models import Job
    if settings.START_SCHEDULER:
        jobs = Job.objects.filter(active=True, scheduled=True, cron__isnull=False)
        for job in jobs:
            add_job(job.slug, job.cron)
        scheduler.start()
    else:
        logger.info("Планировщик скриптов не запущен")

