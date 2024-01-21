import os
import unittest
from http import HTTPStatus

import requests
from dotenv import load_dotenv


class TestNginx(unittest.TestCase):
    """Интеграционные тесты Nginx."""

    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv()
        cls.host = os.getenv("NGINX_HOST")
        cls.port = os.getenv("NGINX_PORT")
        cls.url = "http://%s:%s" % (cls.host, cls.port)
        return super().setUpClass()

    def test_root_response(self):
        """
        Корневой маршрут возвращает успешный ответ,
        ответ содержит шаблон сайта вместо стандартного
        шаблона Nginx, файлы Bootstrap включены в шаблон.
        """
        root_url = f"{self.url}/"
        response = requests.get(root_url)
        status = response.status_code
        text = response.text
        self.assertEqual(status, HTTPStatus.OK)
        self.assertNotIn("nginx", text.lower())
        self.assertIn("bootstrap", text.lower())

    def test_robots_txt(self):
        """Тест получения файла с параметрами индексирования для поисковых систем."""
        robots_txt_url = f"{self.url}/robots.txt"
        response = requests.get(robots_txt_url)
        status = response.status_code
        text = response.text
        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn("User-Agent", text)

    def test_favicon_ico(self):
        """Тест получения фавикона."""
        favicon_ico_url = f"{self.url}/favicon.ico"
        response = requests.get(favicon_ico_url)
        status = response.status_code
        content_type = response.headers.get("Content-Type")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn(content_type, "image/x-icon")


if __name__ == "__main__":
    unittest.main()
