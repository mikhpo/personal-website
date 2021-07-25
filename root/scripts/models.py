from django.db import models
from django.conf import settings
from django.utils.html import format_html

domain = settings.ALLOWED_HOSTS[0]
app = 'scripts'

class Script(models.Model):
    '''Описание скрипта: наименование, предназначение, раписание запуска.'''

    name = models.CharField('Наименование', max_length=255, blank=False)
    description = models.TextField('Описание', blank=True)
    schedule = models.CharField('Расписание', max_length=255, blank=True)
    active = models.BooleanField('Активный', default=True)
    slug = models.SlugField('Слаг для запуска', blank=True)
    command = models.URLField('Полный путь для запуска', blank=True)

    class Meta:
        verbose_name = 'Скрипт'
        verbose_name_plural = 'Скрипты'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        '''
        При сохранении объекта автоматически вычисляется 
        значение поля на основании значения из другого поля.
        '''
        self.command = f'https://{domain}/{app}/{self.slug}/'
        super(Script, self).save(*args, **kwargs)

    def run_script(self):
        '''Преобразует ссылку как текст в кликабельную ссылку.'''
        return format_html(f"<a href='{self.command}'>Запустить</a>")
    run_script.short_description = 'Запуск' 

class Run(models.Model):
    '''Запуск скрипта: время, результат.'''

    class Status(models.IntegerChoices):
        '''Варианты выбора статуса запуска скрипта.'''
        RUNNING = 0, 'Выполняется'
        COMPLETED = 1, 'Завершено'

    script = models.ForeignKey(Script, on_delete=models.CASCADE, blank=True, null=True)
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