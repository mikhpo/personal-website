"""Фабрики для создания объектов приложения авторизации и управления пользователями."""

import factory  # type: ignore[import-untyped]
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """Фабрика для стандартной модели пользователя из django.contrib.auth.models."""

    class Meta:  # noqa: D106
        model = User
        django_get_or_create = ("username", "email")

    username = factory.Faker("user_name")
    password = factory.Faker("password")
    email = factory.Faker("email")

    def __new__(cls, *args, **kwargs) -> "User":
        """Возвращается объект User."""
        return super().__new__(*args, **kwargs)
