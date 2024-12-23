"""Тесты схем для генерации и валидации данных."""

from django.test import SimpleTestCase

from gallery.schemas import ExifData


class TestExifData(SimpleTestCase):
    """Тесты модели данных EXIF."""

    def test_float_fields_accept_int_value(self) -> None:
        """Поля, определенные как float, принимают значения int."""
        exif = ExifData(FNumber=11, ExposureTime=60)
        self.assertIsInstance(exif, ExifData)
