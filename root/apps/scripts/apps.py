from django.apps import AppConfig
import sys
from loguru import logger

class ScriptsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.scripts'
    verbose_name = "скрипты"
