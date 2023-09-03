import os

from django.conf import settings


def str_to_bool(val: str):
    """
    Адаптированная имплементация функции strtobool из стандартной библиотеки distutils.
    """
    if not val:
        return 0
    value = val.lower()
    if value in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif value in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError(f"Неверное значение аргумента {val}")


def list_image_paths():
    """
    Определить пути набора изображений на локальном диске.
    """
    base_dir = settings.BASE_DIR
    media_dir = os.path.join(base_dir, "media")
    images_dir = os.path.join(media_dir, "gallery", "photos")
    image_names = os.listdir(images_dir)
    image_paths = [os.path.join(images_dir, image_name) for image_name in image_names]
    return image_paths
