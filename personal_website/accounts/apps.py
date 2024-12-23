"""Конфигурация приложения для авторизации пользователей."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):  # noqa: D101
    name = "accounts"

    def ready(self) -> None:
        """При инициации приложения подключить сигналы."""
        from accounts import signals  # noqa: F401
