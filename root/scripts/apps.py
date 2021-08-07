from django.apps import AppConfig
import sys
from loguru import logger

class ScriptsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scripts'
    verbose_name = "скрипты"

    def ready(self):
        '''
        Функция выполняется при запуске приложения.
        Если приложение запускается с командой runserver, 
        то инициализуруется запуск планировщика скриптов.
        '''
        from . import scheduler
        if 'runserver' or 'unix:/run/gunicorn.sock' in sys.argv:
            try:
                scheduler.start()
            except:
                logger.exception("Ошибка запуска планировщика")
