"""Настройки запуска тестов при помощи модуля django.test."""

import shutil
from pathlib import Path
from typing import Any

from django.conf import settings
from django.test.runner import DiscoverRunner


class CustomRunner(DiscoverRunner):
    """Альтернативный тестовый раннер для дополнительного управления тестовой средой."""

    def setup_test_environment(self, **kwargs: dict[str, Any]) -> None:
        """
        Создать папку для временных файлов перед глобальным запуском тестов
        и скопировать тестовые изображения в папку для тестирования.
        """
        Path(settings.TEMP_ROOT).mkdir(parents=True, exist_ok=True)
        media_dir = settings.BASE_DIR / "media"
        shutil.copytree(media_dir, settings.TEMP_ROOT, dirs_exist_ok=True)
        return super().setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs: dict[str, Any]) -> None:
        """Удалить папку для временных файлов после глобального завершения тестов."""
        shutil.rmtree(settings.TEMP_ROOT, ignore_errors=True)
        return super().teardown_test_environment(**kwargs)
