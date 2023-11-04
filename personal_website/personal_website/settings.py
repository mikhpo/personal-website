"""Базовый модуль настроек Django-проекта."""
import os
import sys
from pathlib import Path

import environ

from personal_website.utils import NoColorLogFormatter

env = environ.Env(DEBUG=(bool, False))

# Определяется абсолютный путь до текущих директорий для того, чтобы далее в проекте везде использовались относительные пути.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
PROJECT_NAME = BASE_DIR.name

# Определение признака запуска в режиме тестирования.
TEST = any((("test" in sys.argv), ("pytest" in sys.modules)))

# Прочитать переменные окружения из .env файла.
environ.Env.read_env(os.path.join(PROJECT_DIR, ".env"))

# Режим запуска сервера.
DEBUG = env("DEBUG")

# Ключ проекта Django (генерируется автоматически).
SECRET_KEY = env("SECRET_KEY")

# Доменное имя, по которому доступен сайт.
CUSTOM_DOMAIN = env("CUSTOM_DOMAIN")

IP_ADDRESS = env("IP_ADDRESS")

# Список адресов, которые будет обслуживать Django проект. Если не добавлять адрес в этот список, то запросы по данному адресу обрабатываться не будут.
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    IP_ADDRESS,
    CUSTOM_DOMAIN,
    f"www.{CUSTOM_DOMAIN}",
]

# Список приложений = модули Django + модули сообщества + приложения проекта.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "whitenoise.runserver_nostatic",
    "crispy_forms",
    "crispy_bootstrap5",
    "tinymce",
    "adminsortable2",
    "imagekit",
    "django_cleanup.apps.CleanupConfig",
    "accounts",
    "gallery",
    "blog",
    "main",
]

WHITENOISE_MIDDLEWARE = "whitenoise.middleware.WhiteNoiseMiddleware"

# Список промежуточного ПО. Порядок добавления ПО в список необходимо изучать в документации этого ПО.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    WHITENOISE_MIDDLEWARE,
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# При запуске тестов нужно отключить WhiteNoise, так как при запуске тестов режим дебага отключен.
if TEST:
    MIDDLEWARE.remove(WHITENOISE_MIDDLEWARE)

# Относительный путь до urls.py основного модуля Django.
ROOT_URLCONF = f"{PROJECT_NAME}.urls"

WSGI_APPLICATION = f"{PROJECT_NAME}.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

SITE_ID = 1

# Устанавливается язык проекта. В Django встроена русская локализация, которая дает перевод панели администрирования, стандартных форм и рассылки писем.
LANGUAGE_CODE = "ru"

# Устанавливается временная зона.
TIME_ZONE = "Europe/Moscow"

USE_I18N = True

# Да, если мы хотим использовать настройку временной зоны.
USE_TZ = True

# Веб-адрес, по которому будут доступны статические файлы.
STATIC_URL = "/static/"

# Абсолютный путь до папки, в которой собраны статические файлы.
STATIC_ROOT = env("STATIC_ROOT")

# NPM-зависимости в корневом каталоге проекта.
STATICFILES_DIRS = [BASE_DIR / "static", PROJECT_DIR / "node_modules"]

# На проде статические файлы раздаются через WhiteNoise.
WHITENOISE_ROOT = STATIC_ROOT

# Относительный url до медиа-файлов.
MEDIA_URL = "/media/"

# Абсолютный путь до папки с медиа-файлами.
MEDIA_ROOT = env("STORAGE_ROOT")

# Адрес временной папки для тестирования.
TEMP_ROOT = PROJECT_DIR / "temp"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
    "test": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": TEMP_ROOT,
            "base_url": "/media/",
        },
    },
}

# Адрес, на который будет перенаправлен пользователь после авторизации.
LOGIN_REDIRECT_URL = "/"

# Веб-адрес формы авторизации на сайте.
LOGIN_URL = "/accounts/login/"

# Адрес, на который будет перенаправлен пользователь после выхода.
LOGOUT_REDIRECT_URL = "/"

# Веб-адрес для выхода с сайта.
LOGOUT_URL = "/accounts/logout/"

# Лимит на размер загружаемых файлов.
DATA_UPLOAD_MAX_MEMORY_SIZE = None

# С версии Django 3.2 по умолчанию используется новый тип авто-поля для первичного ключа.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Настройки подключения к базам данных.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("PG_NAME"),
        "USER": env("PG_USER"),
        "PASSWORD": env("PG_PASSWORD"),
        "HOST": env("PG_HOST"),
        "PORT": env("PG_PORT"),
    }
}

# Настройки используемого шаблонизатора. Здесь также указан относительный путь до папки с шаблонами проекта.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

# Настройки почтовой службы, используемой для почтовых рассылок.
# В данном проекте используется стандартный функционал Django по восстановлению забытых паролей через почту.
# В связи с этим почтовый адрес является обязательным полем при регистрации нового пользователя.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# настройки модуля Django Crispy Forms, улучшающего отображение стандартных форм Django.
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Настройки TinyMCE - WYSIWYG текстовый редактор.
# В данном Django проекте он используется при создании записей в блог. (через административную панель)
# В данном конфиге определены подключаемые плагины TinyMCE и меню редактора.
TINYMCE_DEFAULT_CONFIG = {
    "cleanup_on_startup": True,
    "custom_undo_redo_levels": 20,
    "selector": "textarea",
    "branding": False,
    "plugins": """
            textcolor save link image media preview codesample contextmenu
            table code lists fullscreen  insertdatetime  nonbreaking
            contextmenu directionality searchreplace wordcount visualblocks
            visualchars code fullscreen autolink lists  charmap print  hr
            anchor pagebreak autoresize
            """,
    "toolbar1": """
            fullscreen preview bold italic underline | fontselect,
            fontsizeselect  | forecolor backcolor | alignleft alignright |
            aligncenter alignjustify | indent outdent | bullist numlist table |
            | link image media | codesample |
            """,
    "toolbar2": """
            visualblocks visualchars |
            charmap hr pagebreak nonbreaking anchor | code |
            """,
    "contextmenu": "formats | link image",
    "menubar": True,
    "statusbar": True,
}

"""
Настройки логирования.
"""
LOGS_ROOT = env("LOGS_ROOT")  # общая папка для сохранения логов
LOG_DIR = os.path.join(LOGS_ROOT, PROJECT_NAME)

# Cоздать директорию для логов, если не существует.
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{asctime}] [{levelname}] {message}",
            "datefmt": "%d.%m.%Y %H:%M:%S",
            "style": "{",
        },
        "simple": {
            "()": NoColorLogFormatter,
            "format": "[{asctime}] [{levelname}] {message}",
            "datefmt": "%d.%m.%Y %H:%M:%S",
            "style": "{",
        },
        "verbose": {
            "()": NoColorLogFormatter,
            "format": "[{asctime}] [{levelname}] [{filename} -> {funcName} -> {lineno}] {message}",
            "datefmt": "%d.%m.%Y %H:%M:%S",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        PROJECT_NAME: {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, f"{PROJECT_NAME}.log"),
            "formatter": "simple",
            "when": "midnight",
            "backupCount": 7,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["django.server", PROJECT_NAME],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": [PROJECT_NAME],
            "level": "INFO",
            "propagate": False,
        },
        PROJECT_NAME: {
            "handlers": ["console", PROJECT_NAME],
            "level": "INFO",
            "propagate": False,
        },
    },
}

"""
Настройки фотогалереи.
"""
# Размер миниатюры в пикселах по наибольшей стороне.
GALLERY_THUMBNAIL_SIZE = 100

# Размер в пикселах по наибольшей стороне для предварительного просмотра.
GALLERY_PREVIEW_SIZE = 1000

# Качество сжатия миниатюр и предварительного просмотра.
GALLERY_RESIZE_QUALITY = 100

# Адрес каталога с фотографиями для тестирования.
TEST_IMAGES_DIR = BASE_DIR / "media" / "gallery" / "photos"
