"""Тесты фабрик для моделей приложения авторизации и управления пользователями."""
from django.contrib.auth.models import User
from django.test import TestCase
from faker import Faker

from accounts.factories import UserFactory

fake = Faker(locale="ru_RU")


class TestUserFactory(TestCase):
    """Тесты фабрики для создания пользователей."""

    def test_user_factory_instance(self) -> None:
        """Фабрика создает объект пользователя."""
        user = UserFactory()
        self.assertIsInstance(user, User)
