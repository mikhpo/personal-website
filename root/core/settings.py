# Модуль настроек Django-проекта.

import os
import json
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# Определяется абсолютный путь до текущей директории для того, чтобы далее в проекте везде использовались относительные пути.
BASE_DIR = Path(__file__).resolve().parent.parent

# Секреты (коды, пароли, логины, ip-адреса) спрятаны в отдельном JSON-файле.
with open(os.path.join(BASE_DIR, 'secrets.json')) as secrets_file:
    secrets = json.load(secrets_file)

def get_secret(setting, secrets=secrets):
    '''
    Функция для получения значения по ключю из JSON файла с секретными данными.
    '''
    try:
        return secrets[setting]
    except KeyError:
        raise ImproperlyConfigured("Необходимо установить значение настройки {}".format(setting))

SECRET_KEY = get_secret('SECRET_KEY') # ключ проекта Django (генерируется автоматически)

'''
Включение (True) и отключение (False) режима отладки. Включать необходимо на этапе разработки и отладки. 
При запуске сайта в производство необходимо режим отладки отключать, так как он выдает пользователю много деталей о структурной организации проекта.
'''
DEBUG = True 

''' 
Список адресов, которые будет обслуживать Django проект. 
Если не добавлять адрес в этот список, то запросы по данному адресу обрабатываться не будут.
В данном случае добавлены три адреса:
1. Доменное имя.
2. IP адрес в локальной сети.
3. IP адрес в глобальной сети.
'''
ALLOWED_HOSTS = [
    '.mikhailpolyakov.com', 
    get_secret('IP_ADDRESS_LOCAL'), 
    get_secret('IP_ADDRESS_PUBLIC'),
    'localhost',
    '127.0.0.1'
]

'''
Список установленных программ. После добавления программы в список Django будет автоматически искать их модули в виртуальном окружении и в каталоге проекта.
Программы в список нужно добавлять в следующем порядке:
1. Дополнительные Python модули.
2. Встроенные модули Django.
3. Приложения пользователя.
'''
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'tinymce',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts.apps.AccountsConfig',
    'main.apps.MainConfig',
    'blog.apps.BlogConfig',
    'scripts.apps.ScriptsConfig',
]

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
ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

'''
Настройки подключения к базам данных. Проект автоматически создается со встроенной базой данных SQLite.
В данном случае было настроено подключение к БД PostgreSQL, которая установлена на том же сервере.
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_secret('DB_NAME'),
        'USER': get_secret('DB_USER'),
        'PASSWORD': get_secret('DB_PASSWORD'),
        'HOST': get_secret('IP_ADDRESS_LOCAL'),
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # абсолютный путь до папки, в которой собраны статические файлы.
WHITENOISE_ROOT = STATIC_ROOT # путь до папки ПО WhiteNoise, который радикально упрощает использование статических файлов в Django-проекте. 
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage' # настройка, необходимая для WhiteNoise

# Медиа файлы - это загружаемые файлы (фото, видео, документы).
MEDIA_URL = '/media/' # Относительный url до медиа-файлов.
MEDIA_ROOT = os.path.join(BASE_DIR,'media') # абсолютный путь до папки с медиа-файлами.

LOGIN_REDIRECT_URL = '/' # адрес, на который будет перенаправлен пользователь после авторизации.
LOGIN_URL = '/accounts/login/' # Веб-адрес формы авторизации на сайте.

LOGOUT_REDIRECT_URL = '/' # адрес, на который будет перенаправлен пользователь после выхода.
LOGOUT_URL = '/accounts/logout/' # Веб-адрес для выхода с сайта.

''' 
Настройки ПО TinyMCE. TinyMCE - это WYSIWYG текстовый редактор. 
В данном Django проекте он используется при создании записей в блог. (через административную панель)
В данном конфиге определены подключаемые плагины TinyMCE и меню редактора.
'''
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

CRISPY_TEMPLATE_PACK = 'bootstrap4' # настройки модуля Django Crispy Forms, улучшающего отображение стандартных форм Django.

'''
Настройки почтовой службы, используемой для почтовых рассылок. 
В данном проекте используется стандартный функционал Django по восстановлению забытых паролей через почту. 
В связи с этим почтовый адрес является обязательным полем при регистрации нового пользователя.
'''
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = get_secret('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

DATA_UPLOAD_MAX_MEMORY_SIZE = None # лимит на размер загружаемых файлов.

# С версии Django 3.2 по умолчанию используется новый тип авто-поля для первичного ключа.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Имя пользователя системы, в которой развернуто приложение.
SERVER_USER = get_secret('SERVER_USER')