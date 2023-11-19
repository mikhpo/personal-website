import datetime
import os

from django.conf import settings
from django.test import SimpleTestCase
from django.utils.crypto import get_random_string
from django.utils.timezone import get_current_timezone

from config.utils import (
    format_local_datetime,
    get_slug,
    has_cyrillic,
    list_file_paths,
    str_to_bool,
)


class StrToBollTests(SimpleTestCase):
    """
    Тестирование утилиты преобразования строки в булево значение.
    """

    def test_none_value_returns_false(self):
        """
        Проверить, что отсутствие значения преобразуется в ложь.
        """
        self.assertFalse(str_to_bool(None))

    def test_positive_value_returns_true(self):
        """
        Проверить, что положительные значения преобразуются в истину.
        """
        for value in ("Yes", "True", "On", "1"):
            self.assertTrue(str_to_bool(value))

    def test_negative_value_returns_false(self):
        """
        Проверить, что отрицательные значения преобразуются в ложь.
        """
        for value in ("No", "False", "Off", "0"):
            self.assertFalse(str_to_bool(value))

    def test_other_value_returns_value_error(self):
        """
        Проверить, что остальные значения вызывают ошибку ValueError.
        """
        value = get_random_string(5)
        with self.assertRaises(ValueError):
            str_to_bool(value)


class HasCyrrillicTests(SimpleTestCase):
    """
    Тестирование утилиты проверки текста на наличие кирилллицы.
    """

    def test_cyrillic_returns_true(self):
        """
        Проверяет, что кириллический текст дает истину.
        """
        cyrillic_text = "Тестовый текст"
        cyrillic = has_cyrillic(cyrillic_text)
        self.assertTrue(cyrillic)

    def test_latin_returns_false(self):
        """
        Проверяет, что латинский текст дает ложь.
        """
        latin_text = "Test text"
        cyrillic = has_cyrillic(latin_text)
        self.assertFalse(cyrillic)

    def test_mixed_returns_true(self):
        """
        Проверяет, что смешанный текст дает истину.
        """
        mixed_text = "Test Текст"
        cyrillic = has_cyrillic(mixed_text)
        self.assertTrue(cyrillic)


class TranslitSlugTests(SimpleTestCase):
    """
    Тестирование утилиты создания транслитерированных текстов.
    """

    def test_slug_translit_when_cyrillic(self):
        """
        Проверяет, что из кириллицы слаг создается транслитом.
        """
        text = "Тоскана"
        slug = get_slug(text)
        self.assertEqual(slug, "toskana")

    def test_slug_no_translit_when_no_cyrillic(self):
        """
        Проверяет, что из латиницы слаг создается стандартным методом.
        """
        text = "Tuscany"
        slug = get_slug(text)
        self.assertEqual(slug, "tuscany")


class ListImagesPathTests(SimpleTestCase):
    """
    Тестирование утилиты поиска абсолютных путей тестовых фотографий.
    """

    def test_paths_exist(self):
        """
        Проверить, что возвращенные пути существуют.
        """
        image_paths_list = list_file_paths(settings.TEST_IMAGES_DIR)
        self.assertIsInstance(image_paths_list, list)
        for image_path in image_paths_list:
            self.assertTrue(os.path.exists(image_path))


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
