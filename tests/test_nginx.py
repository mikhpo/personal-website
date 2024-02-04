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
        """Тест получения файла с параметрами индексирования для поисковых систем."""
        robots_txt_url = f"{self.url}/robots.txt"
        response = requests.get(robots_txt_url, timeout=10)
        status = response.status_code
        text = response.text
        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn("User-Agent", text)

    def test_favicon_ico(self) -> None:
        """Тест получения фавикона."""
        favicon_ico_url = f"{self.url}/favicon.ico"
        response = requests.get(favicon_ico_url, timeout=10)
        status = response.status_code
        content_type = response.headers.get("Content-Type")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn(content_type, "image/x-icon")


if __name__ == "__main__":
    unittest.main()
