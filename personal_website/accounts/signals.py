"""Логирование действий пользователей по авторизации на сайте."""
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

logger = logging.getLogger(settings.PROJECT_NAME)


@receiver(user_logged_in)
def post_login(sender, request, user: User, **kwargs):
    if request:
        ip = request.META.get("HTTP_X_REAL_IP")
        if user:
            username = user.username
            logger.info(f"Пользователь {username} авторизовался с IP-адреса {ip}")


@receiver(user_logged_out)
def post_logout(sender, request, user: User, **kwargs):
    if request:
        ip = request.META.get("HTTP_X_REAL_IP")
        if user:
            username = user.username
            logger.info(f"Пользователь {username} c IP-адресом {ip} вышел")


@receiver(user_login_failed)
def post_login_fail(sender, credentials, request, **kwargs):
    if request:
        ip = request.META.get("HTTP_X_REAL_IP")
        username = credentials.get("username", None)
        logger.warning(
            f"Неудачная попытка авторизации пользователя {username} с IP-адреса {ip}"
        )
