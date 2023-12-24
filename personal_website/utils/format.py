import datetime
import locale

from django.utils import timezone


def format_local_datetime(date_time: datetime.datetime):
    """
    Преобразует дату-время в строку с учетом локализации и временной зоны.
    """
    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
    if timezone.is_aware(date_time):
        date_time = timezone.localtime(date_time)
    date_time_displayed = "{dt.day} {dt:%B} {dt.year} г. {dt.hour}:{dt:%M}".format(
        dt=date_time
    )
    return date_time_displayed
