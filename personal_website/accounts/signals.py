'''Логирование действий пользователей по авторизации на сайте.'''
import logging
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_login_failed, user_logged_out

logger = logging.getLogger('personal_website')

@receiver(user_logged_in)
def post_login(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    username = user.username
    logger.info(f'Пользователь {username} авторизовался с IP-адреса {ip}')

@receiver(user_logged_out)
def post_logout(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    username = user.username
    logger.info(f'Пользователь {username} c IP-адресом {ip} вышел')

@receiver(user_login_failed)
def post_login_fail(sender, credentials, request, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    username = credentials.get('username', None)
    logger.warning(f'Неудачная попытка авторизации пользователя {username} с IP-адреса {ip}')