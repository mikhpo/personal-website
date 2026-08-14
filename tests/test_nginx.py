"""Интеграционное тестирование прокси-сервера Nginx."""

import os
import unittest
from http import HTTPStatus

import requests
from dotenv import load_dotenv


class TestNginx(unittest.TestCase):
    """Интеграционные тесты Nginx."""

    @classmethod
    def setUpClass(cls) -> None:
        """Определить параметры подключения к Nginx."""
        load_dotenv()
        cls.port = os.getenv("NGINX_PORT")
        cls.url = f"http://localhost:{cls.port}"
        return super().setUpClass()

    def test_root_response(self) -> None:
        """Тестирование доступности корневого маршрута.

        Корневой маршрут возвращает успешный ответ,
        ответ содержит шаблон сайта вместо стандартного
        шаблона Nginx, файлы Bootstrap включены в шаблон.
        """
        root_url = f"{self.url}/"
        response = requests.get(root_url, timeout=10)
        status = response.status_code
        text = response.text
        self.assertEqual(status, HTTPStatus.OK)
        self.assertNotIn("nginx", text.lower())
        self.assertIn("bootstrap", text.lower())

    def test_robots_txt(self) -> None:
        """Тест получения файла с параметрами индексирования для поисковых систем.

        Файл обслуживается статическим хранилищем: nginx отвечает постоянным
        редиректом, цель редиректа доступна и содержит параметры индексирования.
        """
        robots_txt_url = f"{self.url}/robots.txt"
        response = requests.get(robots_txt_url, allow_redirects=False, timeout=10)
        status = response.status_code
        self.assertEqual(status, HTTPStatus.MOVED_PERMANENTLY)
        location = response.headers.get("Location", "")
        self.assertTrue(location.endswith("robots.txt"))
        target = self._resolve_location(location)
        target_response = requests.get(target, timeout=10)
        self.assertEqual(target_response.status_code, HTTPStatus.OK)
        self.assertIn("User-Agent", target_response.text)

    def test_favicon_ico(self) -> None:
        """Тест получения фавикона.

        Файл обслуживается статическим хранилищем: nginx отвечает постоянным
        редиректом, цель редиректа доступна и имеет тип изображения иконки.
        """
        favicon_ico_url = f"{self.url}/favicon.ico"
        response = requests.get(favicon_ico_url, allow_redirects=False, timeout=10)
        status = response.status_code
        self.assertEqual(status, HTTPStatus.MOVED_PERMANENTLY)
        location = response.headers.get("Location", "")
        self.assertTrue(location.endswith("favicon.ico"))
        target = self._resolve_location(location)
        target_response = requests.get(target, timeout=10)
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
