from django.db import models
from django.utils.html import format_html

class Script(models.Model):
    '''Описание скрипта: наименование, предназначение, раписание запуска.'''

    name = models.CharField('Наименование', max_length=255, blank=False)
    description = models.TextField('Описание', blank=True)
    schedule = models.CharField('Расписание', max_length=255, blank=True)
    active = models.BooleanField('Активный', default=True)
    command = models.URLField('Запуск', blank=True)

    class Meta:
        verbose_name = 'Скрипт'
        verbose_name_plural = 'Скрипты'

    def __str__(self):
        return self.name

    def run_script(self):
        '''Преобразует ссылку как текст в кликабельную ссылку.'''
        return format_html("<a href='%s'>Запустить</a>" % (self.command))
    run_script.short_description = 'Запуск' 

class Run(models.Model):
    '''Запуск скрипта: время, результат.'''

    class Status(models.IntegerChoices):
        '''Варианты выбора статуса запуска скрипта.'''
        RUNNING = 0, 'Выполняется'
        COMPLETED = 1, 'Завершено'

    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    start = models.DateTimeField('Время запуска', auto_now_add=True)
    status = models.IntegerField('Статус', choices=Status.choices)
    end = models.DateTimeField('Время завершения', blank=True, null=True)
    success = models.BooleanField('Успешный', blank=True, null=True)
    result = models.TextField('Результат', blank=True)
    log = models.TextField('Журнал', blank=True)

    class Meta:
        verbose_name = 'Запуск'
        verbose_name_plural = 'Запуски'

    def __str__(self):
        return f'{self.script}: {self.start}'