'''Базовый модуль настроек Django-проекта.'''
import os
import re
import json
import logging
from pathlib import Path
from platform import uname
from django.core.exceptions import ImproperlyConfigured

# Определение среды запуска, от которой зависят переменные окружения и конфигурационные параметры.
# Определяем систему по параметрам хоста. Для разных сред используются разные значения секретов.
# Имя секрета включает в себя указание на среду: PROD, DEV, TEST.
SYSTEM = uname().release
if 'microsoft' in SYSTEM:
    ENV = 'DEV'
    DEBUG = True
    DOMAIN = '127.0.0.1:8000'
elif 'raspi' in SYSTEM:
    ENV = 'DEV'
    DEBUG = True
elif 'generic' in SYSTEM:
    ENV = 'PROD'
    DEBUG = False
else:
    DEBUG = True

# Определяется абсолютный путь до текущей директории для того, чтобы далее в проекте везде использовались относительные пути.
BASE_DIR = Path(__file__).resolve().parent.parent

# Секреты (коды, пароли, логины, IP-адреса) спрятаны в отдельных JSON-файлах.
# Для разных сред используются разные JSON-файлы.
with open(os.path.join(BASE_DIR, 'secrets.json')) as secrets_file:
    SECRETS = json.load(secrets_file)

def GET_SECRET(setting: str, secrets: dict = SECRETS) -> str:
    '''Функция для получения значения по ключю из JSON файлов с секретными данными.'''
    try:
        return secrets[setting]
    except KeyError:
        raise ImproperlyConfigured("Необходимо установить значение настройки {}".format(setting))

# Ключ проекта Django (генерируется автоматически).
SECRET_KEY = GET_SECRET('SECRET_KEY') 

# Имя пользователя системы, в которой развернуто приложение.
SERVER_USER = GET_SECRET(f'SERVER_USER_{ENV}')

# Путь до интерпретатора Python.
PYTHON_PATH = os.path.join(BASE_DIR, '..', '.venv', 'bin', 'python')

# Путь до модуля manage.py.
MANAGE_PATH = os.path.join(BASE_DIR, 'manage.py')

# Список адресов, которые будет обслуживать Django проект. 
# Если не добавлять адрес в этот список, то запросы по данному адресу обрабатываться не будут.
# В данном случае добавлены три адреса:
# 1. Доменное имя.
# 2. IP адрес в локальной сети.
# 3. IP адрес в глобальной сети.
# Для корректного запуска скриптов необходимо доменное имя указывать первым элементом списка.
ALLOWED_HOSTS = [
    GET_SECRET('DOMAIN_NAME'),
    GET_SECRET('WWW_DOMAIN_NAME'),
    GET_SECRET('IP_ADDRESS_LOCAL'), 
    GET_SECRET(f'IP_ADDRESS_PUBLIC_{ENV}'),
    'localhost',
    '127.0.0.1'
]

INTERNAL_IPS = [
    '127.0.0.1',
    GET_SECRET('IP_ADDRESS_LOCAL'),
    GET_SECRET('IP_ADDRESS_PUBLIC_DEV'),
]

# Модули проекта Django.
DJANGO_PACKAGES = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
]

# Модули для Django от сообщества.
COMMUNITY_PACKAGES = [
    'whitenoise.runserver_nostatic',
    'tinymce',
    'crispy_forms',
]

# Локальные приложения проекта.
PROJECT_APPS = [
    'apps.accounts.apps.AccountsConfig',
    'apps.main.apps.MainConfig',
    'apps.blog.apps.BlogConfig',
    'apps.scripts.apps.ScriptsConfig',
]

# Итоговый список приложений - объединение предыдущих трёх.
INSTALLED_APPS = DJANGO_PACKAGES + COMMUNITY_PACKAGES + PROJECT_APPS

# Список промежуточного ПО. Порядок добавления ПО в список необходимо изучать в документации этого ПО.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Относительный путь до urls.py основного модуля Django.
ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

SITE_ID = 1

# Устанавливается язык проекта. В Django встроена русская локализация, которая дает перевод панели администрирования, стандартных форм и рассылки писем.
LANGUAGE_CODE = 'ru'

# Устанавливается временная зона.
TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

# Да, если мы хотим использовать настройку временной зоны.
USE_TZ = True

# Статические файлы - это фавиконы, CSS, модули JavaScript, библиотеки Node. 
STATIC_URL = '/static/' # веб-адрес, по которому будут доступны статические файлы
STATIC_ROOT = os.path.join(BASE_DIR, 'static') # абсолютный путь до папки, в которой собраны статические файлы.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'node_modules'),
) # npm-зависимости в корневом каталоге проекта
WHITENOISE_ROOT = STATIC_ROOT # путь до папки ПО WhiteNoise, который радикально упрощает использование статических файлов в Django-проекте. 
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage' # настройка, необходимая для WhiteNoise

# Медиа файлы - это загружаемые файлы (фото, видео, документы).
MEDIA_URL = '/media/' # Относительный url до медиа-файлов.
MEDIA_ROOT = os.path.join(BASE_DIR,'media') # абсолютный путь до папки с медиа-файлами.

LOGIN_REDIRECT_URL = '/' # адрес, на который будет перенаправлен пользователь после авторизации.
LOGIN_URL = '/accounts/login/' # Веб-адрес формы авторизации на сайте.

LOGOUT_REDIRECT_URL = '/' # адрес, на который будет перенаправлен пользователь после выхода.
LOGOUT_URL = '/accounts/logout/' # Веб-адрес для выхода с сайта.

DATA_UPLOAD_MAX_MEMORY_SIZE = None # лимит на размер загружаемых файлов.

# С версии Django 3.2 по умолчанию используется новый тип авто-поля для первичного ключа.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки подключения к базам данных.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': GET_SECRET(f'DB_NAME_{ENV}'),
        'USER': GET_SECRET('DB_USER'),
        'PASSWORD': GET_SECRET('DB_PASSWORD'),
        'HOST': GET_SECRET(f'DB_HOST_{ENV}'),
        'PORT': GET_SECRET(f'DB_PORT_{ENV}'),
    }
}

# Настройки используемого шаблонизатора. Здесь также указан относительный путь до папки с шаблонами проекта.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

# Настройки почтовой службы, используемой для почтовых рассылок. 
# В данном проекте используется стандартный функционал Django по восстановлению забытых паролей через почту. 
# В связи с этим почтовый адрес является обязательным полем при регистрации нового пользователя.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = GET_SECRET('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = GET_SECRET('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

CRISPY_TEMPLATE_PACK = 'bootstrap4' # настройки модуля Django Crispy Forms, улучшающего отображение стандартных форм Django.

# Настройки TinyMCE - WYSIWYG текстовый редактор. 
# В данном Django проекте он используется при создании записей в блог. (через административную панель)
# В данном конфиге определены подключаемые плагины TinyMCE и меню редактора.
TINYMCE_DEFAULT_CONFIG = {
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'branding': False,
    'plugins': '''
            textcolor save link image media preview codesample contextmenu
            table code lists fullscreen  insertdatetime  nonbreaking
            contextmenu directionality searchreplace wordcount visualblocks
            visualchars code fullscreen autolink lists  charmap print  hr
            anchor pagebreak autoresize
            ''',
    'toolbar1': '''
            fullscreen preview bold italic underline | fontselect,
            fontsizeselect  | forecolor backcolor | alignleft alignright |
            aligncenter alignjustify | indent outdent | bullist numlist table |
            | link image media | codesample |
            ''',
    'toolbar2': '''
            visualblocks visualchars |
            charmap hr pagebreak nonbreaking anchor | code |
            ''',
    'contextmenu': 'formats | link image',
    'menubar': True,
    'statusbar': True,
}

# Настройки логирования.
LOGS_DIR = os.path.join(BASE_DIR, 'logs') # папка для сохранения логов
os.makedirs(LOGS_DIR, exist_ok=True) # создать папку для логов, если она не существует

class ColoredVerboseFormatter(logging.Formatter):
    """Цветное форматирование детализированных сообщений."""

    # Список цветов в соответствии с кодировкой ANSI.
    grey = "\x1b[38;20m"
    cyan = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    # Формат записи.
    format = "[%(server_time)s] [%(levelname)s] [%(filename)s -> %(funcName)s -> %(lineno)s] %(message)s"

    # Карта соответствия уровню сообщения и формату записи с цветовой кодировкой.
    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: cyan + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class NonColoredSimpleFormatter(logging.Formatter):
    """Бесцветное сокращенное форматирование для сохранения в лог-файлы."""

    # Регулярное выражение, соответствующее спец-символам ANSI-кодировки.
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")

    def format(self, record):
        '''Подстановка атрибутов лог-сообщения в указанный формат и удаление ANSI-кодировки регулярным выражением.'''
        try:
            return "[%s] [%s] %s" % (
                record.server_time,
                record.levelname,
                re.sub(self.ansi_re, "", record.msg % record.args),
            )
        except: 
            return re.sub(self.ansi_re, "", record.msg % record.args)

class NonColoredVerboseFormatter(logging.Formatter):
    """Бесцветное детализированное форматирование для сохранения в лог-файлы."""

    # Регулярное выражение, соответствующее спец-символам ANSI-кодировки.
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")

    def format(self, record):
        '''Подстановка атрибутов лог-сообщения в указанный формат и удаление ANSI-кодировки регулярным выражением.'''
        try:
            return "[%s] [%s] [%s -> %s -> %s] %s" % (
                record.server_time,
                record.levelname,
                record.filename,
                record.funcName,
                record.lineno,
                re.sub(self.ansi_re, "", record.msg % record.args),
            )
        except: 
            return re.sub(self.ansi_re, "", record.msg % record.args)
             

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
            'format': '[{server_time}] [{levelname}] {message}',
            'style': '{',
        },
        'non_colored_simple': {
            '()': NonColoredSimpleFormatter
        },
        'non_colored_verbose': {
            '()': NonColoredVerboseFormatter
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'requests_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'requests.log'),
            'formatter': 'non_colored_simple'
        },
        'users_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'users.log'),
            'formatter': 'non_colored_simple'
        },
        'blog_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'blog.log'),
            'formatter': 'non_colored_verbose'
        },
        'scripts_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'scripts.log'),
            'formatter': 'non_colored_verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server', 'requests_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['requests_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.contrib.auth': {
            'handlers': ['console', 'users_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.blog': {
            'handlers': ['console', 'blog_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.scripts': {
            'handlers': ['console', 'scripts_log'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}