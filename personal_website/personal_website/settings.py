'''Базовый модуль настроек Django-проекта.'''
import os
import re
import sys
import logging
from pathlib import Path
import environ

env = environ.Env(DEBUG = (bool, False))

# Определяется абсолютный путь до текущих директорий для того, чтобы далее в проекте везде использовались относительные пути.
BASE_DIR = Path(__file__).resolve().parent.parent

# Прочитать переменные окружения из .env файла.
environ.Env.read_env(os.path.join(BASE_DIR, '..', '.env'))

# Режим запуска сервера.
DEBUG = env('DEBUG')

# Ключ проекта Django (генерируется автоматически).
SECRET_KEY = env('SECRET_KEY')

# Список адресов, которые будет обслуживать Django проект. Если не добавлять адрес в этот список, то запросы по данному адресу обрабатываться не будут.
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.68',
    '46.138.246.69',
    "mikhailpolyakov.com",
    "www.mikhailpolyakov.com",
]

# Список приложений = модули Django + модули сообщества + приложения проекта.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'whitenoise.runserver_nostatic',
    'crispy_forms',
    'tinymce',
    'accounts.apps.AccountsConfig',
    'main.apps.MainConfig',
    'blog.apps.BlogConfig',
]

whitenoise_middleware = 'whitenoise.middleware.WhiteNoiseMiddleware'

# Список промежуточного ПО. Порядок добавления ПО в список необходимо изучать в документации этого ПО.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    whitenoise_middleware,
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# При запуске тестов нужно отключить WhiteNoise, так как при запуске тестов режим дебага отключен.
if 'test' in sys.argv:
    MIDDLEWARE.remove(whitenoise_middleware)

# Относительный путь до urls.py основного модуля Django.
ROOT_URLCONF = 'personal_website.urls'

WSGI_APPLICATION = 'personal_website.wsgi.application'

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
STATICFILES_DIRS = [os.path.join(BASE_DIR, '..', 'node_modules')] # npm-зависимости в корневом каталоге проекта
WHITENOISE_ROOT = STATIC_ROOT # на проде статические файлы раздаются через WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage' # настройка, необходимая для WhiteNoise

# Медиа файлы - это загружаемые файлы (фото, видео, документы).
MEDIA_URL = '/media/' # Относительный url до медиа-файлов.
MEDIA_ROOT = os.path.join(Path(BASE_DIR).parent.parent.parent, 'Storages', 'personal_website') # абсолютный путь до папки с медиа-файлами.

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
        'NAME': env('PG_NAME'),
        'USER': env('PG_USER'),
        'PASSWORD': env('PG_PASSWORD'),
        'HOST': env('PG_HOST'),
        'PORT': env('PG_PORT'),
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
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
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

'''Настройки логирования.'''
LOGS_DIR = os.path.join(BASE_DIR, '..', 'logs') # общая папка для сохранения логов

# Список директорий для ведения логов.
LOG_DIRS = [
    LOGS_DIR, 
    os.path.join(LOGS_DIR, 'personal_website'),
]

# Cоздать директории для логов, если они не существуют.
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
        'personal_website': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'personal_website', 'personal_website.log'),
            'formatter': 'simple',
            'when': 'midnight',
            'backupCount': 7
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server', 'personal_website'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['personal_website'],
            'level': 'INFO',
            'propagate': False,
        },
        'personal_website': {
            'handlers': ['console', 'personal_website'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}
