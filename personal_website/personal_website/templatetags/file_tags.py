"""
Кастомный тэг для проверки фактического наличия файла в файловом хранилище приложения.

Для использования тэгов из данного модуля в шаблоне необходимо вверху шаблона объявить:

    {% load file_tags %}

Examples:
    ```
    {% if photo.image.name|file_exists %}
        ...
    {% endif %}
    ```
"""

from django import template

from personal_website.storages import select_storage

register = template.Library()
storage = select_storage()


@register.filter
def file_exists(file_name: str) -> bool:
    """Проверяет наличие файла по заданному пути в файловом хранилище.

    Args:
        file_name (str): имя файла, включая относительный путь.

    Returns:
        bool: существует файл по указанному пути или нет.
    """
    return storage.exists(file_name)
