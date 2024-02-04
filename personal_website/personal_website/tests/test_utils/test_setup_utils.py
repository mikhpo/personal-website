"""Тесты вспомогательных функци для конфигурирования проекта."""
from django.test import SimpleTestCase
from django.utils.crypto import get_random_string

from personal_website.utils import str_to_bool


class StrToBollTests(SimpleTestCase):
    """Тестирование утилиты преобразования строки в булево значение."""

    def test_none_value_returns_false(self) -> None:
        """Проверить, что отсутствие значения преобразуется в ложь."""
        self.assertFalse(str_to_bool(None))

    def test_positive_value_returns_true(self) -> None:
        """Проверить, что положительные значения преобразуются в истину."""
        for value in ("Yes", "True", "On", "1"):
            self.assertTrue(str_to_bool(value))

    def test_negative_value_returns_false(self) -> None:
        """Проверить, что отрицательные значения преобразуются в ложь."""
        for value in ("No", "False", "Off", "0"):
            self.assertFalse(str_to_bool(value))

    def test_other_value_returns_value_error(self) -> None:
        """Проверить, что остальные значения вызывают ошибку ValueError."""
        value = get_random_string(5)
        with self.assertRaises(ValueError):
            str_to_bool(value)
