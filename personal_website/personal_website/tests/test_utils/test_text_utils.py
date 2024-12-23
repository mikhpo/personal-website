"""Тесты вспомогательных функций для работы с текстом."""

import random

from django.test import SimpleTestCase

from personal_website.utils import generate_random_text, get_slug, has_cyrillic


class TestGenerateRandomText(SimpleTestCase):
    """Тесты утилиты для генерации случайного текста."""

    def test_generate_random_text(self) -> None:
        """Утилита возвращает текст, состоящий из заданного количества слова, разделенных пробелами."""
        random_count = random.randint(1, 50)
        random_text = generate_random_text(random_count)
        words = random_text.split(" ")
        self.assertEqual(random_count, len(words))


class HasCyrrillicTests(SimpleTestCase):
    """Тестирование утилиты проверки текста на наличие кирилллицы."""

    def test_cyrillic_returns_true(self) -> None:
        """Проверяет, что кириллический текст дает истину."""
        cyrillic_text = "Тестовый текст"
        cyrillic = has_cyrillic(cyrillic_text)
        self.assertTrue(cyrillic)

    def test_latin_returns_false(self) -> None:
        """Проверяет, что латинский текст дает ложь."""
        latin_text = "Test text"
        cyrillic = has_cyrillic(latin_text)
        self.assertFalse(cyrillic)

    def test_mixed_returns_true(self) -> None:
        """Проверяет, что смешанный текст дает истину."""
        mixed_text = "Test Текст"
        cyrillic = has_cyrillic(mixed_text)
        self.assertTrue(cyrillic)


class TranslitSlugTests(SimpleTestCase):
    """Тестирование утилиты создания транслитерированных текстов."""

    def test_slug_translit_when_cyrillic(self) -> None:
        """Проверяет, что из кириллицы слаг создается транслитом."""
        text = "Тоскана"
        slug = get_slug(text)
        self.assertEqual(slug, "toskana")

    def test_slug_no_translit_when_no_cyrillic(self) -> None:
        """Проверяет, что из латиницы слаг создается стандартным методом."""
        text = "Tuscany"
        slug = get_slug(text)
        self.assertEqual(slug, "tuscany")
