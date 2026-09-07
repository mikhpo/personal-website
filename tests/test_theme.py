"""Интеграционное тестирование темы сайта в реальном браузере."""

import os
import unittest
from typing import Literal

from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

# Цвет фона страницы задается base.css через --bs-tertiary-bg: константы Bootstrap 5.3.
LIGHT_BACKGROUND = "rgb(248, 249, 250)"
DARK_BACKGROUND = "rgb(43, 48, 53)"


class TestTheme(unittest.TestCase):
    """Интеграционные тесты определения темы до первой отрисовки страницы.

    Скрипт backend/staticfiles/js/theme.js задает атрибут data-bs-theme
    на <html> до применения стилей. Проверяется приоритет темы: явный выбор
    пользователя в localStorage, затем системная тема (эмуляция
    prefers-color-scheme), затем светлая, а также отрисовка фона страницы.
    """

    browser: Browser
    playwright: Playwright
    context: BrowserContext
    page: Page

    @classmethod
    def setUpClass(cls) -> None:
        """Запустить браузер и определить параметры подключения к стеку."""
        load_dotenv()
        cls.port = os.getenv("HTTPS_PORT", default="443")
        cls.url = f"https://localhost:{cls.port}"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        """Остановить браузер."""
        cls.browser.close()
        cls.playwright.stop()
        return super().tearDownClass()

    def setUp(self) -> None:
        """Открыть контекст браузера со страницей.

        ignore_https_errors - осознанное решение для интеграционного теста:
        в локальном стеке nginx обслуживает HTTPS self-signed сертификатом
        (task dev-cert), как и в тестах прокси.
        """
        self.context = self.browser.new_context(ignore_https_errors=True)
        self.page = self.context.new_page()
        return super().setUp()

    def tearDown(self) -> None:
        """Закрыть контекст браузера."""
        self.context.close()
        return super().tearDown()

    def _open_main(self) -> None:
        """Открыть главную страницу локального стека."""
        self.page.goto(f"{self.url}/main/", wait_until="load")

    def _set_stored_theme(self, theme: str) -> None:
        """Задать сохраненный выбор темы пользователя до загрузки страниц."""
        self.page.add_init_script(f"window.localStorage.setItem('theme', '\"{theme}\"')")

    def _emulate_system_theme(self, scheme: Literal["dark", "light"]) -> None:
        """Эмулировать системную тему ОС (prefers-color-scheme)."""
        self.page.emulate_media(color_scheme=scheme)

    def _current_theme(self) -> str:
        """Прочитать значение атрибута data-bs-theme на <html>."""
        return self.page.evaluate("document.documentElement.getAttribute('data-bs-theme')")

    def _background_color(self) -> str:
        """Прочитать вычисленный цвет фона страницы."""
        return self.page.evaluate("getComputedStyle(document.body).backgroundColor")

    def test_stored_dark_theme_overrides_light_system(self) -> None:
        """Тестирование перекрытия системной темы сохраненным выбором "dark"."""
        self._set_stored_theme("dark")
        self._emulate_system_theme("light")
        self._open_main()
        self.assertEqual(self._current_theme(), "dark")

    def test_stored_light_theme_overrides_dark_system(self) -> None:
        """Тестирование перекрытия системной темы сохраненным выбором "light"."""
        self._set_stored_theme("light")
        self._emulate_system_theme("dark")
        self._open_main()
        self.assertEqual(self._current_theme(), "light")

    def test_system_dark_theme_without_stored_choice(self) -> None:
        """Тестирование применения темной системной темы без сохраненного выбора."""
        self._emulate_system_theme("dark")
        self._open_main()
        self.assertEqual(self._current_theme(), "dark")

    def test_system_light_theme_without_stored_choice(self) -> None:
        """Тестирование применения светлой системной темы без сохраненного выбора."""
        self._emulate_system_theme("light")
        self._open_main()
        self.assertEqual(self._current_theme(), "light")

    def test_invalid_stored_value_falls_back_to_system_theme(self) -> None:
        """Тестирование игнорирования поврежденного значения в localStorage.

        Значение, не являющееся "light" или "dark", обрабатывается
        как отсутствие явного выбора: применяется системная тема.
        """
        self._set_stored_theme("blue")
        self._emulate_system_theme("dark")
        self._open_main()
        self.assertEqual(self._current_theme(), "dark")

    def test_background_color_follows_stored_theme(self) -> None:
        """Тестирование отрисовки фона страницы в выбранной теме.

        Сквозная проверка: выбор задается на загруженной странице,
        после перезагрузки скрипт применяет его до отрисовки, и стили
        Bootstrap реагируют на атрибут цветом фона.
        """
        self._open_main()
        self.page.evaluate("window.localStorage.setItem('theme', '\"dark\"')")
        self.page.reload()
        self.assertEqual(self._background_color(), DARK_BACKGROUND)

        self.page.evaluate("window.localStorage.setItem('theme', '\"light\"')")
        self.page.reload()
        self.assertEqual(self._background_color(), LIGHT_BACKGROUND)


if __name__ == "__main__":
    unittest.main()
