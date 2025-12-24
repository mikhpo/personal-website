"""Тесты кастомных тэгов."""

from pathlib import Path

from django.test import SimpleTestCase
from faker import Faker
from faker_file.providers.txt_file import TxtFileProvider  # type:ignore[import-untyped]

from personal_website.storages import FakerFileStorageAdapter
from personal_website.templatetags.file_tags import file_exists

fake = Faker()


class TestFileExistsTag(SimpleTestCase):
    """Тесты тэга проверки наличия файла в хранилище."""

    def test_file_exists(self) -> None:
        """Файл действительно существует."""
        reletive_path = Path(__file__).resolve().stem
        faker_storage = FakerFileStorageAdapter(rel_path=reletive_path)
        txt_file: str = TxtFileProvider(fake).txt_file(storage=faker_storage, raw=False)
        self.assertTrue(file_exists(txt_file))
