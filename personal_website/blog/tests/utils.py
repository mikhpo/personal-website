import random
import locale
import datetime
from django.utils.crypto import get_random_string

def generate_random_text(word_count: int):
    '''Генерирует случайный текст, состоящий из заданного количества слов.'''
    random_length = random.randint(5, 50)
    random_word = get_random_string(random_length)
    random_text = (random_word + ' ') * word_count
    return random_text

def localize_datetime(date_time: datetime.datetime):
    '''Преобразует дату-время в строку с учетом локализации и временной зоны.'''
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    date_time_displayed = date_time.astimezone(timezone).strftime("%d %B %Y г. %H:%M")
    return date_time_displayed
