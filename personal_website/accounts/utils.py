"""Вспомогательные функции системы авторизации пользователей."""

import random

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


def generate_unique_username() -> str:
    """Создает пользователя с уникальным логином."""
    random_length = random.randint(5, 10)  # noqa: S311
    random_string = get_random_string(random_length)
    while User.objects.filter(username=random_string).exists():
        random_string = get_random_string(random_length)
    return random_string
