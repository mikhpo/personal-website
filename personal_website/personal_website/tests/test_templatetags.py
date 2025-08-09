"""Тесты кастомных тэгов."""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase
from faker import Faker
from faker_file.providers.txt_file import TxtFileProvider  # type: ignore[import-untyped]
from faker_file.storages.filesystem import FileSystemStorage  # type: ignore[import-untyped]

from personal_website.templatetags.file_tags import file_exists

fake = Faker()


class TestFileExistsTag(SimpleTestCase):
    """Тесты тэга проверки наличия файла в хранилище."""

    def test_file_exists(self) -> None:
        """Файл действительно существует."""
        txt_file: str = TxtFileProvider(fake).txt_file(
            storage=FileSystemStorage(
                root_path=settings.TEMP_ROOT,
                rel_path=Path(__file__).resolve().stem,
            ),
            raw=False,
        )
        self.assertTrue(file_exists(txt_file))
