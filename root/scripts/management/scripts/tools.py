def format_time(seconds):
    '''Преобразует период из секунд в минуты в формате 00.00.'''
    minutes = seconds / 60
    return "{:.2f}".format(minutes).replace(",", " ")