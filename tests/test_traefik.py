"""Интеграционное тестирование прокси-сервера Traefik."""

import os
import unittest
import warnings
from http import HTTPStatus
from pathlib import Path

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
        # verify=False - осознанное решение для интеграционного теста:
        # в dev-среде без certresolver Traefik обслуживает HTTPS встроенным
        # self-signed сертификатом. Для продакшена с сертификатами Let's Encrypt
        # проверка должна быть включена (см. докстринг класса).
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
        http_port = os.getenv("TRAEFIK_HTTP_PORT", default="80")
        http_url = f"http://localhost:{http_port}/"
        response = requests.get(http_url, allow_redirects=False, timeout=10)
        status = response.status_code
        self.assertEqual(status, HTTPStatus.MOVED_PERMANENTLY)
        location = response.headers.get("Location", "")
        self.assertTrue(location.startswith("https://"))

    def test_robots_txt(self) -> None:
        """Тест получения файла с параметрами индексирования для поисковых систем.

        Файл доступен через статическое хранилище. Режим раздачи зависит
        от STORAGE_TYPE: при filesystem файл обслуживается WhiteNoise
        напрямую (200), при s3 приложение отвечает постоянным редиректом
        (301) на адрес бакета. В обоих случаях файл доступен и содержит
        параметры индексирования.
        """
        robots_txt_url = f"{self.url}/robots.txt"
        response = requests.get(robots_txt_url, allow_redirects=False, timeout=10, verify=False)
        if response.status_code == HTTPStatus.MOVED_PERMANENTLY:
            location = response.headers.get("Location", "")
            self.assertTrue(location.endswith("robots.txt"))
            target = self._resolve_location(location)
            response = requests.get(target, timeout=10, verify=False)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("User-Agent", response.text)

    def test_favicon_ico(self) -> None:
        """Тест получения фавикона.

        Файл доступен через статическое хранилище. Режим раздачи зависит
        от STORAGE_TYPE: при filesystem файл обслуживается WhiteNoise
        напрямую (200), при s3 приложение отвечает постоянным редиректом
        (301) на адрес бакета. В обоих случаях файл доступен и имеет тип
        изображения иконки.
        """
        favicon_ico_url = f"{self.url}/favicon.ico"
        response = requests.get(favicon_ico_url, allow_redirects=False, timeout=10, verify=False)
        if response.status_code == HTTPStatus.MOVED_PERMANENTLY:
            location = response.headers.get("Location", "")
            self.assertTrue(location.endswith("favicon.ico"))
            target = self._resolve_location(location)
            response = requests.get(target, timeout=10, verify=False)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content_type = response.headers.get("Content-Type")
        self.assertEqual(content_type, "image/x-icon")

    def test_media_file(self) -> None:
        """Тест раздачи медиафайлов filesystem-хранилища.

        При STORAGE_TYPE=filesystem медиа раздает контейнер media
        (профиль media, nginx): Traefik маршрутизирует запросы /media/
        в него, минуя приложение. Проверяется сквозной путь - файл,
        записанный в каталог хранилища на хосте, доступен через прокси.
        При STORAGE_TYPE=s3 медиа отдает бакет, и маршрут /media/
        не используется - тест пропускается.
        """
        if os.getenv("STORAGE_TYPE", "filesystem") != "filesystem":
            self.skipTest("медиа раздаются объектным хранилищем (STORAGE_TYPE=s3)")
        storage_root = Path(os.getenv("STORAGE_ROOT", "storage"))
        media_file = storage_root / "traefik_media_test.txt"
        media_file.parent.mkdir(parents=True, exist_ok=True)
        media_file.write_text("media test", encoding="utf-8")
        try:
            media_url = f"{self.url}/media/{media_file.name}"
            response = requests.get(media_url, timeout=10, verify=False)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response.text, "media test")
        finally:
            media_file.unlink(missing_ok=True)

    def _resolve_location(self, location: str) -> str:
        """Преобразовать значение заголовка Location в абсолютный адрес."""
        if location.startswith(("http://", "https://")):
            return location
        return f"{self.url}{location}"


if __name__ == "__main__":
    unittest.main()
