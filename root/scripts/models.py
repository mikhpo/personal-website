from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html
from croniter import croniter
import datetime
from django.core.exceptions import ValidationError

def cron_validator(value):
    '''Функция для проверки корректности крон-выражения.'''
    if not value:
        return
    if not croniter.is_valid(value):
        raise ValidationError("Некорректное крон-выражение")

def calculate_command_path(slug):
    '''Определяет полный путь для запуска скрипта.'''
    debug = settings.DEBUG
    if debug: protocol = 'http'
    else: protocol = 'https'
    domain = settings.DOMAIN
    return f'{protocol}://{domain}/scripts/command/{slug}/'

class Job(models.Model):
    '''Описание скрипта: наименование, предназначение, раписание запуска.'''

    name = models.CharField('Наименование', max_length=255, blank=False)
    description = models.TextField('Описание', blank=True)
    cron = models.CharField('Крон-выражение', blank=True, max_length=255, validators=[cron_validator])
    schedule = models.CharField('Расписание', max_length=255, blank=True)
    last_run = models.DateTimeField('Последний запуск', blank=True, null=True)
    active = models.BooleanField('Активный', default=True)
    scheduled = models.BooleanField('Автоматический', default=False)
    manual = models.BooleanField('Ручной', default=False)
    slug = models.SlugField('Слаг для запуска', blank=True)
    command = models.URLField('Полный путь для запуска', blank=True)

    class Meta:
        verbose_name = 'Скрипт'
        verbose_name_plural = 'Скрипты'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        '''
        При сохранении объекта автоматически вычисляется значение поля на основании значения из другого поля. 
        Если крон-выражение было изменено, то раписание скрипта изменяется автоматически.
        '''
        from .scheduler import add_job, reschedule_job
        # Если у объекта уже есть первичный ключ, т.е. он был создан ранее.
        if self.pk:
            old = Job.objects.get(pk=self.pk)
            # Если старый и новый слаг отличаются, то необходимо переопределить полный путь для команды.
            if self.slug != old.slug:
                self.command = calculate_command_path(self.slug)
            # Если старое и новое крон-выражения отличаются, то необходимо перезапустить планировщик.
            if (self.cron != old.cron) and settings.START_SCHEDULER:
                reschedule_job(self.slug, self.cron)
        # Если это вновь созданный объект.            
        else:
            if settings.START_SCHEDULER: 
                add_job(self.slug, self.cron)
            self.command = calculate_command_path(self.slug)
        super(Job, self).save(*args, **kwargs)

    def run_script(self):
        '''Преобразует ссылку как текст в кликабельную ссылку.'''
        if self.manual:
            return format_html(f"<a href='{self.command}'>Запустить</a>")
        else:
            return None

    def next_run(self):
        '''Определение по крон-выражению времени следующего запуска.'''
        now = timezone.localtime(timezone.now())
        next_datetime = croniter(self.cron, now).get_next(datetime.datetime)
        return next_datetime

    next_run.short_description = 'Следующий запуск'
    run_script.short_description = 'Запустить' 

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