"""Тесты вспомогательных утилит галереи."""

import os
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from faker import Faker
from faker_file.providers.jpeg_file import JpegFileProvider  # type: ignore[import-untyped]
from faker_file.providers.txt_file import TxtFileProvider  # type: ignore[import-untyped]
from faker_file.storages.filesystem import FileSystemStorage  # type: ignore[import-untyped]

from gallery.apps import GalleryConfig
from gallery.factories import AlbumFactory, ExifDataFactory, PhotoFactory
from gallery.models import Photo
from gallery.schemas import ExifData
from gallery.utils import (
    is_image,
    move_photo_image,
    photo_image_upload_full_path,
    photo_image_upload_path,
    read_exif,
    write_exif,
)
from personal_website.utils import list_file_paths

FAKER = Faker()
FS_STORAGE = FileSystemStorage(root_path=os.getenv("TEMP_ROOT"), rel_path=GalleryConfig.name)


class GalleryUtilsTests(TestCase):
    """Тесты утилит приложения галереи."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные."""
        cls.tuscany_album = AlbumFactory(name="Тоскана")
        cls.langtang_album = AlbumFactory(name="Лангтанг")

        # Создать фотографии в базе данных из картинок в директории проекта.
        test_dir = os.getenv("TEMP_ROOT", default=settings.PROJECT_DIR / "temp")
        test_images_dir = Path(test_dir) / "gallery" / "photos"
        images = list_file_paths(test_images_dir)
        for image in images:
            if "Tuscany" in image:
                album = cls.tuscany_album
            elif "Langtang" in image:
                album = cls.langtang_album
            else:
                msg = "Нужно создать новый тестовый альбом"
                raise Exception(msg)  # noqa: TRY002
            PhotoFactory(image=image, name=None, album=album)

        return super().setUpTestData()

    def test_photo_image_upload_path(self) -> None:
        """Проверка функции получения относительного пути загрузки файла изображения."""
        first_photo = Photo.objects.first()
        self.assertIsInstance(first_photo, Photo)
        if first_photo:
            relative_path = photo_image_upload_path(first_photo, "test.jpg")
            self.assertIsInstance(relative_path, str)
            absolute = Path(relative_path).is_absolute()
            self.assertFalse(absolute)

    def test_photo_image_upload_full_path(self) -> None:
        """Проверка функции получения абсолютного пути загрузки файла изображения."""
        first_photo = Photo.objects.first()
        self.assertIsInstance(first_photo, Photo)
        if first_photo:
            relative_path = photo_image_upload_full_path(first_photo, "test.jpg")
            absolute = Path(relative_path).is_absolute()
            self.assertIsInstance(relative_path, str)
            self.assertTrue(absolute)

    def test_move_photo_image(self) -> None:
        """Проверка функции перемещения фотографии по новому адресу."""
        with self.subTest("Файл по старому адресу существует"):
            photo = Photo.objects.filter(album=self.tuscany_album).first()
            self.assertIsInstance(photo, Photo)
            if photo:
                old_path = photo.image.path
                self.assertTrue(Path(old_path).exists())

                with self.subTest("Файл по старому адресу более не существует, но теперь существует по новому адресу"):
                    photo.album = self.langtang_album
                    new_path = move_photo_image(photo, photo.image.path)
                    self.assertFalse(Path(old_path).exists())
                    self.assertTrue(Path(new_path).exists())


class TestIsImage(SimpleTestCase):
    """Тесты утилиты для проверки на то, является ли файл изображением."""

    def test_true_image(self) -> None:
        """Изображение распознается как изображение."""
        jpeg_file = JpegFileProvider(FAKER).jpeg_file(storage=FS_STORAGE, raw=False)
        jpeg_file_path = FS_STORAGE.abspath(jpeg_file)
        result = is_image(jpeg_file_path)
        self.assertTrue(result)

    def test_false_image(self) -> None:
        """Текстовый файл не распознается как изображение."""
        txt_file = TxtFileProvider(FAKER).txt_file(storage=FS_STORAGE, raw=False)
        txt_file_path = FS_STORAGE.abspath(txt_file)
        result = is_image(txt_file_path)
        self.assertFalse(result)


class TestExifUtils(SimpleTestCase):
    """Тесты утилит для работы с EXIF."""

    def setUp(self) -> None:
        """Подготовка тестового изображения."""
        jpeg_file = JpegFileProvider(FAKER).jpeg_file(storage=FS_STORAGE, raw=False)
        self.jpeg_file_path = FS_STORAGE.abspath(jpeg_file)
        return super().setUp()

    def test_read_exif(self) -> None:
        """Утилита для чтения EXIF из изображения возвращает объект с данными."""
        exif_data = read_exif(self.jpeg_file_path)
        self.assertIsInstance(exif_data, ExifData)

    def test_write_exif(self) -> None:
        """Утилита для записи EXIF в изображение сохраняет данные EXIF в файл."""
        # Перед вызовом функции прочитать данные EXIF из изображения
        # и убедиться, что проверяемый атрибут не содержит значения.
        exif = read_exif(self.jpeg_file_path)
        self.assertIsNone(exif.model)

        # Вызвать функцию, передав случайно сгенерированный набор данных.
        exif_data = ExifDataFactory()
        write_exif(self.jpeg_file_path, exif_data)

        # После вызова функции повторно прочитать данные EXIF из изображения
        # и убедиться, что проверяемый атрибут содержит значение, которое
        # соответствует значению из сгенерированного набора данных.
        exif = read_exif(self.jpeg_file_path)
        self.assertIsNotNone(exif.model)
        self.assertEqual(exif.model, exif_data.model)
