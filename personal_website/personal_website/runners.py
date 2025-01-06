"""Настройки запуска тестов при помощи модуля django.test."""

import os
import shutil
from pathlib import Path
from typing import Any

from django.conf import settings
from django.test.runner import DiscoverRunner

temp_dir = os.getenv("TEMP_ROOT", default=Path(settings.PROJECT_DIR) / "temp")


class CustomRunner(DiscoverRunner):
    """Альтернативный тестовый раннер для дополнительного управления тестовой средой."""

    def setup_test_environment(self, **kwargs: dict[str, Any]) -> None:
        """
        Создать папку для временных файлов перед глобальным запуском тестов
        и скопировать тестовые изображения в папку для тестирования.
        """
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        media_dir = settings.BASE_DIR / "media"
        shutil.copytree(media_dir, temp_dir, dirs_exist_ok=True)
        return super().setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs: dict[str, Any]) -> None:
        """Удалить папку для временных файлов после глобального завершения тестов."""
        shutil.rmtree(temp_dir, ignore_errors=True)
        return super().teardown_test_environment(**kwargs)
