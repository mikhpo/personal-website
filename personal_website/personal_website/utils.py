import datetime
import locale
import logging
import os
import random
import re

from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from pytils import translit


def str_to_bool(val: str):
    """
    Адаптированная имплементация функции strtobool из стандартной библиотеки distutils.
    """
    if not val:
        return False
    value = val.lower()
    if value in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif value in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"Неверное значение аргумента {val}")


def is_running_in_container():
    """
    Проверяет, запущено ли приложение внутри контейнера и возвращает логическое значение.
    """
    if os.path.exists("/proc/1/cgroup"):
        return True
    else:
        return False


def format_local_datetime(date_time: datetime.datetime):
    """
    Преобразует дату-время в строку с учетом локализации и временной зоны.
    """
    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
    if timezone.is_aware(date_time):
        date_time = timezone.localtime(date_time)
    date_time_displayed = "{dt.day} {dt:%B} {dt.year} г. {dt.hour}:{dt:%M}".format(dt=date_time)
    return date_time_displayed


class NoColorLogFormatter(logging.Formatter):
    """
    Бесцветное форматирование для вывода логов в файлы.
    Обесцвечивание достигается путем удаления символов соответствующей ANSI-кодировки.
    Дополнительно создается атрибут текущего времени в формате "01.01.2001".
    """

    # Регулярное выражение, соответствующее символам ANSI-кодировки.
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")

    def format(self, record):
        if self.uses_asctime() and not hasattr(record, "asctime"):
            record.asctime = self.formatTime(record, "%d.%m.%Y %H:%M:%S")
        record.msg = re.sub(self.ansi_re, "", record.msg)
        return super().format(record)

    def uses_asctime(self):
        return self._fmt.find("{asctime}") >= 0


def list_file_paths(files_dir: str):
    """
    Определить пути набора набора файлов в указанном каталоге.

    Аргументы:
        files_dir (str): путь до файлов.

    Возвращает:
        Список полных путей до файлов.
    """
    names = os.listdir(files_dir)
    paths = [os.path.join(files_dir, name) for name in names]
    file_paths = [path for path in paths if os.path.isfile(path)]
    return file_paths


def calculate_path_size(path: str) -> dict:
    """
    Определение размера файла или каталога по указанному пути
      с автоматическим определением единцы измерения.

    Аргументы:
        path (str): путь до файла или каталога.

    Возвращает:
        Словарь, содержащий значение, единицу измерения и сообщение. Например: \

            ```python
            {"value": 500, "unit": "КБ", "message": "500 КБ"}
            ```
    """
    units = ("Б", "КБ", "МБ", "ГБ", "ТБ")

    # Способ определения размера дампа зависит от типа пути: файл или каталог.
    if os.path.isdir(path):
        size = 0
        for path, _, files in os.walk(path):
            for file in files:
                filepath = os.path.join(path, file)
                size += os.path.getsize(filepath)
    else:
        size = os.path.getsize(path)

    # Определение единцы измерения размера дампа. Значение округляется до целого числа.
    for unit in units:
        if size < 1024:
            value = int(size)
            return {"value": value, "unit": unit, "message": f"{value} {unit}"}
        size /= 1024


def has_cyrillic(text: str):
    """
    Проверяет наличие в тексте кириллических символов.
    """
    return bool(re.search("[а-яА-Я]", text))


def get_slug(text: str):
    """
    Создает слаг из текста.
    """
    if has_cyrillic:
        return translit.slugify(text)
    else:
        return slugify(text)


def get_unique_slug(instance, text):
    """
    Создает уникальный слаг, уникальный для данного класса.
    """
    model = instance.__class__
    slug = get_slug(text)
    n = 1
    while model.objects.filter(slug=slug).exists():
        n += 1
        slug = f"{slug}-{n}"
    return slug


def generate_random_text(word_count: int):
    """
    Генерирует случайный текст, состоящий из заданного количества слов.
    """
    random_length = random.randint(5, 50)
    random_word = get_random_string(random_length)
    random_text = (random_word + " ") * word_count
    return random_text
