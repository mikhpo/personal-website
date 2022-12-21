import random
import locale
import datetime
from django.utils import timezone
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
    local_date_time = timezone.localtime(date_time)
    date_time_displayed = "{dt.day} {dt:%B} {dt.year} г. {dt.hour}:{dt:%M}".format(dt=local_date_time)
    return date_time_displayed