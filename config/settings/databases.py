'''Настройки подключения к базам данных.''' 
from .secrets import get_secret

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_secret('DB_NAME'),
        'USER': get_secret('DB_USER'),
        'PASSWORD': get_secret('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': get_secret('DB_PORT'),
    }
}