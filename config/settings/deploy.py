'''Параметры развертывания проекта на сервере.'''
from platform import uname
from .secrets import get_secret

# Список адресов, которые будет обслуживать Django проект. 
# Если не добавлять адрес в этот список, то запросы по данному адресу обрабатываться не будут.
# В данном случае добавлены три адреса:
# 1. Доменное имя.
# 2. IP адрес в локальной сети.
# 3. IP адрес в глобальной сети.
# Для корректного запуска скриптов необходимо доменное имя указывать первым элементом списка.
ALLOWED_HOSTS = [
    get_secret('DOMAIN_NAME'),
    get_secret('WWW_DOMAIN_NAME'),
    get_secret('IP_ADDRESS_LOCAL'), 
    get_secret('IP_ADDRESS_PUBLIC'),
    'localhost',
    '127.0.0.1'
]

# Включение и отключение режима отладки. 
# Включать необходимо на этапе разработки и тестирования. 
# При запуске сайта в производство необходимо режим отладки отключать, 
# так как он выдает пользователю много деталей о структурной организации проекта.
# Режим отладки включен, если приложение развернуто на системе для разработки (WSL), 
# и выключен, если приложение развернуто на целевой системе (Raspberry PI).
SYSTEM = uname().release
if 'microsoft' in SYSTEM:
    DEBUG = True
    DOMAIN = '127.0.0.1:8000'
elif 'raspi' in SYSTEM:
    DEBUG = False
    DOMAIN = ALLOWED_HOSTS[0]
elif 'generic' in SYSTEM:
    DEBUG = False
    DOMAIN = ALLOWED_HOSTS[0]
else:
    DEBUG = True
    DOMAIN = ALLOWED_HOSTS[0]

# Настройка, определяющая, следует ли запускать планировщик скриптов.
START_SCHEDULER = False