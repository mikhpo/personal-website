"""Тесты кастомных тэгов."""
import os
from pathlib import Path

from django.test import SimpleTestCase
from faker import Faker
from faker_file.providers.txt_file import TxtFileProvider
from faker_file.storages.filesystem import FileSystemStorage

from personal_website.templatetags.file_tags import file_exists

fake = Faker()


class TestFileExistsTag(SimpleTestCase):
    """Тесты тэга проверки наличия файла в хранилище."""

    def test_file_exists(self) -> None:
        """Файл действительно существует."""
        txt_file: str = TxtFileProvider(fake).txt_file(
            storage=FileSystemStorage(
                root_path=os.getenv("TEMP_ROOT"),
                rel_path=Path(__file__).resolve().stem,
            ),
            raw=False,
        )
        self.assertTrue(file_exists(txt_file))
