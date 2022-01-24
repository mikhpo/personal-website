'''Базовый модуль настроек Django-проекта.'''
import os
from .paths import BASE_DIR

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
WHITENOISE_ROOT = STATIC_ROOT # путь до папки ПО WhiteNoise, который радикально упрощает использование статических файлов в Django-проекте. 
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage' # настройка, необходимая для WhiteNoise

# Медиа файлы - это загружаемые файлы (фото, видео, документы).
MEDIA_URL = '/media/' # Относительный url до медиа-файлов.
MEDIA_ROOT = os.path.join(BASE_DIR,'media') # абсолютный путь до папки с медиа-файлами.

LOGIN_REDIRECT_URL = '/' # адрес, на который будет перенаправлен пользователь после авторизации.
LOGIN_URL = '/accounts/login/' # Веб-адрес формы авторизации на сайте.

LOGOUT_REDIRECT_URL = '/' # адрес, на который будет перенаправлен пользователь после выхода.
LOGOUT_URL = '/accounts/logout/' # Веб-адрес для выхода с сайта.

CRISPY_TEMPLATE_PACK = 'bootstrap4' # настройки модуля Django Crispy Forms, улучшающего отображение стандартных форм Django.

DATA_UPLOAD_MAX_MEMORY_SIZE = None # лимит на размер загружаемых файлов.

# С версии Django 3.2 по умолчанию используется новый тип авто-поля для первичного ключа.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'