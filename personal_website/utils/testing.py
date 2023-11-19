import shutil
from pathlib import Path

from django.conf import settings


def copy_test_images():
    """
    Скопировать тестовые изображения в папку для тестирования.
    """
    Path(settings.TEST_IMAGES_DIR).mkdir(parents=True, exist_ok=True)
    shutil.copytree(settings.TEST_IMAGES_DIR, settings.TEMP_ROOT, dirs_exist_ok=True)
    return settings.TEMP_ROOT


def remove_test_dir():
    """
    Удалить временную папку для тестирования.
    """
    shutil.rmtree(settings.TEMP_ROOT, ignore_errors=True)
