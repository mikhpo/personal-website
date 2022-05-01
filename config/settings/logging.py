'''Настройки логирования.'''
import os
import re
import logging
from .base import BASE_DIR

LOGS_DIR = os.path.join(BASE_DIR, 'logs') # общая папка для сохранения логов
REQUESTS_LOGS_DIR = os.path.join(LOGS_DIR, 'requests')
USERS_LOGS_DIR = os.path.join(LOGS_DIR, 'users')
BLOG_LOGS_DIR = os.path.join(LOGS_DIR, 'blog')
SCRIPTS_LOGS_DIR = os.path.join(LOGS_DIR, 'scripts')
LOG_DIRS = [LOGS_DIR, REQUESTS_LOGS_DIR, USERS_LOGS_DIR, BLOG_LOGS_DIR, SCRIPTS_LOGS_DIR]
# Cоздать папкb для логов, если они не существуют.
for dir in LOG_DIRS:
    os.makedirs(dir, exist_ok=True)

class NoColorLogFormatter(logging.Formatter):
    '''
    Бесцветное форматирование для вывода логов в файлы. 
    Обесцвечивание достигается путем удаления символов соответствующей ANSI-кодировки.
    Дополнительно создается атрибут текущего времени в формате "01.01.2001".
    '''
    # Регулярное выражение, соответствующее символам ANSI-кодировки.
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")

    def format(self, record):
        if self.uses_asctime() and not hasattr(record, 'asctime'):
            record.asctime = self.formatTime(record, '%d.%m.%Y %H:%M:%S')
        record.msg = re.sub(self.ansi_re, "", record.msg)
        return super().format(record)

    def uses_asctime(self):
        return self._fmt.find('{asctime}') >= 0


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{asctime}] [{levelname}] {message}',
            'datefmt': '%d.%m.%Y %H:%M:%S',
            'style': '{',
        },
        'simple': {
            '()': NoColorLogFormatter,
            'format': '[{asctime}] [{levelname}] {message}',
            'datefmt': '%d.%m.%Y %H:%M:%S',
            'style': '{',
        },
        'verbose': {
            '()': NoColorLogFormatter,
            'format': '[{asctime}] [{levelname}] [{filename} -> {funcName} -> {lineno}] {message}',
            'datefmt': '%d.%m.%Y %H:%M:%S',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'requests_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'requests', 'requests.log'),
            'formatter': 'simple',
            'when': 'midnight'
        },
        'users_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'users', 'users.log'),
            'formatter': 'simple',
            'when': 'midnight'
        },
        'blog_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'blog', 'blog.log'),
            'formatter': 'simple',
            'when': 'midnight'
        },
        'scripts_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'scripts', 'scripts.log'),
            'formatter': 'verbose',
            'when': 'midnight'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server', 'requests_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['requests_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        'users_logger': {
            'handlers': ['console', 'users_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        'blog_logger': {
            'handlers': ['console', 'blog_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        'scripts_logger': {
            'handlers': ['console', 'scripts_handler'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}