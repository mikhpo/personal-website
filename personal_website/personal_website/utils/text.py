import random
import re

from django.utils.crypto import get_random_string
from django.utils.text import slugify
from pytils import translit


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
