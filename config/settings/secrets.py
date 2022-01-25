'''Секреты (коды, пароли, логины, ip-адреса) спрятаны в отдельном JSON-файле.'''
import os
import json
from django.core.exceptions import ImproperlyConfigured
from .paths import BASE_DIR

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

# Ключ проекта Django (генерируется автоматически).
SECRET_KEY = get_secret('SECRET_KEY') 

# Имя пользователя системы, в которой развернуто приложение.
SERVER_USER = get_secret('SERVER_USER')
