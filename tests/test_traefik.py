"""Интеграционное тестирование прокси-сервера Traefik."""

import os
import unittest
import warnings
from http import HTTPStatus

import requests
from dotenv import load_dotenv


class TestTraefik(unittest.TestCase):
    """Интеграционные тесты Traefik.

    Запросы выполняются по протоколу HTTPS: в dev-среде без certresolver
    Traefik обслуживает соединения встроенным self-signed сертификатом,
    поэтому проверка сертификата отключается.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Определить параметры подключения к Traefik."""
        load_dotenv()
        cls.port = os.getenv("TRAEFIK_HTTPS_PORT", default="443")
        cls.url = f"https://localhost:{cls.port}"
        # Отключить предупреждения о непроверяемом self-signed сертификате.
        warnings.filterwarnings("ignore", category=UserWarning)
        return super().setUpClass()

    def test_root_response(self) -> None:
        """Тестирование доступности корневого маршрута.

        Корневой маршрут возвращает успешный ответ,
        ответ содержит шаблон сайта вместо стандартной
        страницы прокси-сервера, файлы Bootstrap включены в шаблон.
        """
        root_url = f"{self.url}/"
        response = requests.get(root_url, timeout=10, verify=False)
        status = response.status_code
        text = response.text
        self.assertEqual(status, HTTPStatus.OK)
        self.assertNotIn("traefik", text.lower())
        self.assertIn("bootstrap", text.lower())

    def test_http_redirect(self) -> None:
        """Тестирование редиректа HTTP на HTTPS.

        Входная точка web отвечает постоянным редиректом
        на одноименный маршрут входной точки websecure.
        """
        http_port = os.getenv("NGINX_PORT", default="80")
        http_url = f"http://localhost:{http_port}/"
        response = requests.get(http_url, allow_redirects=False, timeout=10)
        status = response.status_code
        self.assertEqual(status, HTTPStatus.MOVED_PERMANENTLY)
        location = response.headers.get("Location", "")
        self.assertTrue(location.startswith("https://"))

    def test_robots_txt(self) -> None:
        """Тест получения файла с параметрами индексирования для поисковых систем.

        Файл обслуживается статическим хранилищем: приложение отвечает постоянным
        редиректом, цель редиректа доступна и содержит параметры индексирования.
        """
        robots_txt_url = f"{self.url}/robots.txt"
        response = requests.get(robots_txt_url, allow_redirects=False, timeout=10, verify=False)
        status = response.status_code
        self.assertEqual(status, HTTPStatus.MOVED_PERMANENTLY)
        location = response.headers.get("Location", "")
        self.assertTrue(location.endswith("robots.txt"))
        target = self._resolve_location(location)
        target_response = requests.get(target, timeout=10, verify=False)
        self.assertEqual(target_response.status_code, HTTPStatus.OK)
        self.assertIn("User-Agent", target_response.text)

    def test_favicon_ico(self) -> None:
        """Тест получения фавикона.

        Файл обслуживается статическим хранилищем: приложение отвечает постоянным
        редиректом, цель редиректа доступна и имеет тип изображения иконки.
        """
        favicon_ico_url = f"{self.url}/favicon.ico"
        response = requests.get(favicon_ico_url, allow_redirects=False, timeout=10, verify=False)
        status = response.status_code
        self.assertEqual(status, HTTPStatus.MOVED_PERMANENTLY)
        location = response.headers.get("Location", "")
        self.assertTrue(location.endswith("favicon.ico"))
        target = self._resolve_location(location)
        target_response = requests.get(target, timeout=10, verify=False)
        self.assertEqual(target_response.status_code, HTTPStatus.OK)
        content_type = target_response.headers.get("Content-Type")
        self.assertIn(content_type, "image/x-icon")

    def _resolve_location(self, location: str) -> str:
        """Преобразовать значение заголовка Location в абсолютный адрес."""
        if location.startswith(("http://", "https://")):
            return location
        return f"{self.url}{location}"


if __name__ == "__main__":
    unittest.main()
