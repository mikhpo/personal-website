'''
Модуль для моделей планировщика скриптов. 
Приложение использует две модели: 
- Скрипт (описание и параметры запуска скрипта).
- Выполнение (статус и история выполнения скрипта).
'''
import subprocess
import datetime
from croniter import croniter
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html
from django.core.exceptions import ValidationError

class Job(models.Model):
    '''Описание скрипта: наименование, предназначение, раписание запуска.'''

    def cron_validator(value: str):
        '''Функция для проверки корректности крон-выражения.'''
        if not value:
            return
        if not croniter.is_valid(value):
            raise ValidationError("Некорректное крон-выражение")

    name = models.CharField('Наименование', max_length=255, blank=False)
    description = models.TextField('Описание', blank=True)
    cron = models.CharField('Крон-выражение', blank=True, max_length=255, validators=[cron_validator])
    schedule = models.CharField('Расписание', max_length=255, blank=True)
    last_run = models.DateTimeField('Последний запуск', blank=True, null=True)
    active = models.BooleanField('Активный', default=True)
    scheduled = models.BooleanField('Автоматический', default=False)
    manual = models.BooleanField('Ручной', default=False)
    slug = models.SlugField('Слаг для запуска', blank=True)

    class Meta:
        verbose_name = 'Скрипт'
        verbose_name_plural = 'Скрипты'

    def __str__(self):
        return self.name

    def url(self):
        '''Формирует кликабельную ссылку для запуска команды.'''
        if self.manual:
            env = settings.ENV # протокол зависит от среды запуска
            if env == "PROD": protocol = 'https'
            else: protocol = 'http'
            domain = settings.DOMAIN
            return format_html(f"<a href='{protocol}://{domain}/scripts/command/{self.slug}/'>Запустить</a>")
        else:
            return None

    def next_run(self):
        '''Определение по крон-выражению времени следующего запуска.'''
        now = timezone.localtime(timezone.now())
        next_datetime = croniter(self.cron, now).get_next(datetime.datetime)
        return next_datetime

    next_run.short_description = 'Следующий запуск'
    url.short_description = 'Запустить' 

    def run(self):
        '''
        Функция для запуска административной команды Django.
        Запускает команду в отдельном процессе, используя контекст Django.
        Не дожидается окончания выполнения команды.
        '''
        arguments = [
            settings.PYTHON_PATH, 
            settings.MANAGE_PATH, 
            self.slug
        ]
        return subprocess.Popen(arguments)

class Execution(models.Model):
    '''Запуск скрипта: время, результат.'''

    class RunStatus(models.IntegerChoices):
        '''Варианты выбора статуса запуска скрипта.'''
        RUNNING = 0, 'Выполняется'
        COMPLETED = 1, 'Завершено'

    class ReturnStatus(models.IntegerChoices):
        '''Варианты выбора статуса выполнения скрипта.'''
        UNSUCCESSFULL = 0, 'Нет'
        SUCCESSFULL = 1, 'Да'

    job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=True, null=True)
    start = models.DateTimeField('Время запуска', auto_now_add=True)
    status = models.IntegerField('Статус', blank=True, null=True, choices=RunStatus.choices)
    end = models.DateTimeField('Время завершения', blank=True, null=True)
    success = models.BooleanField('Успешный', blank=True, null=True, choices=ReturnStatus.choices)
    result = models.TextField('Результат', blank=True)

    class Meta:
        verbose_name = 'Выполнение'
        verbose_name_plural = 'Выполнения'
        ordering = ['-start']

    def __str__(self):
        start_time = timezone.localtime(self.start)
        return f'{self.job}: {start_time.strftime("%d.%m.%Y %H:%M")}'
        