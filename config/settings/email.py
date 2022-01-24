'''
Настройки почтовой службы, используемой для почтовых рассылок. 
В данном проекте используется стандартный функционал Django по восстановлению забытых паролей через почту. 
В связи с этим почтовый адрес является обязательным полем при регистрации нового пользователя.
'''
from .secrets import get_secret
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = get_secret('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False