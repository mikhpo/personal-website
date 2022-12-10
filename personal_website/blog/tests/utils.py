import random
from django.utils.crypto import get_random_string

def generate_random_text(word_count: int):
    '''Генерирует случайный текст, состоящий из заданного количества слов.'''
    random_length = random.randint(5, 50)
    random_word = get_random_string(random_length)
    random_text = (random_word + ' ') * word_count
    return random_text