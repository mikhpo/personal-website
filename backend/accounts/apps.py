"""Конфигурация приложения для авторизации пользователей."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):  # noqa: D101
    name = "accounts"

    def ready(self) -> None:
        """При инициации приложения подключить сигналы и аудит пользователей."""
        # Нужно импортировать сигналы внутри метода ready для того,
        # чтобы избежать циклических зависимостей
        from auditlog.registry import auditlog  # noqa: PLC0415
        from django.contrib.auth import get_user_model  # noqa: PLC0415

        from accounts import signals  # noqa: F401, PLC0415

        auditlog.register(
            get_user_model(),
            m2m_fields={"groups", "user_permissions"},
            exclude_fields=["last_login"],
            mask_fields=["password"],
        )
