import datetime

from django.test import SimpleTestCase
from django.utils.timezone import get_current_timezone

from utils import format_local_datetime


class FormatLocalDatetimeTests(SimpleTestCase):
    """
    Тесты утилиты форматирования даты-времени в локальное представление.
    """

    def test_date_time_displayed(self):
        """
        Должно бтыь возвращена дата и время в локализованном формате.
        """
        date_time_value = datetime.datetime(
            2001, 1, 1, 1, 1, 1, tzinfo=get_current_timezone()
        )
        target_format = "1 января 2001 г. 1:01"
        date_time_displayed = format_local_datetime(date_time_value)
        self.assertEqual(date_time_displayed, target_format)
