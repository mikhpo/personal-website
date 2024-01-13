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

import logging
import re


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
