"""Настройки запуска тестов при помощи модуля django.test."""

from typing import Any

from django.test.runner import DiscoverRunner

from personal_website.utils import setup_test_environment, teardown_test_environment


class CustomRunner(DiscoverRunner):
    """Альтернативный тестовый раннер для дополнительного управления тестовой средой."""

    def setup_test_environment(self, **kwargs: dict[str, Any]) -> None:
        """
        Создать папку для временных файлов перед глобальным запуском тестов
        и скопировать тестовые изображения в папку для тестирования.
        """
        setup_test_environment()
        return super().setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs: dict[str, Any]) -> None:
        """Удалить папку для временных файлов после глобального завершения тестов."""
        teardown_test_environment()
        return super().teardown_test_environment(**kwargs)
