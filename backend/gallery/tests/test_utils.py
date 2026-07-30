"""Тесты вспомогательных утилит галереи."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase
from faker import Faker
from faker_file.providers.jpeg_file import JpegFileProvider  # type: ignore[import-untyped]
from faker_file.providers.txt_file import TxtFileProvider  # type: ignore[import-untyped]
from PIL.TiffImagePlugin import IFDRational

from gallery.apps import GalleryConfig
from gallery.factories import AlbumFactory, ExifDataFactory, PhotoFactory
from gallery.models import Photo
from gallery.schemas import ExifData
from gallery.utils import (
    compute_datetime_taken,
    exif_value_to_json,
    is_image,
    move_photo_image,
    photo_image_upload_full_path,
    photo_image_upload_path,
    read_exif,
    write_exif,
)
from personal_website.storages import FakerFileStorageAdapter, StorageType, select_storage
from personal_website.utils import list_file_paths

FAKER = Faker()
FS_STORAGE = FakerFileStorageAdapter(rel_path=GalleryConfig.name)
storage: StorageType = select_storage()


class GalleryUtilsTests(TestCase):
    """Тесты утилит приложения галереи."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные."""
        cls.tuscany_album = AlbumFactory(name="Тоскана")
        cls.langtang_album = AlbumFactory(name="Лангтанг")

        # Создать фотографии в базе данных из картинок в директории проекта.
        test_images_dir = "gallery/photos"
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
            self.assertIsInstance(relative_path, str)
            # Проверяем, что путь является абсолютным в контексте используемого хранилища
            # Для файловой системы это будет абсолютный путь ОС, для S3 - путь вида "s3://bucket/path"
            absolute = storage.is_absolute(relative_path)
            self.assertTrue(absolute)

    def test_move_photo_image(self) -> None:
        """Проверка функции перемещения фотографии по новому адресу."""
        with self.subTest("Файл по старому адресу существует"):
            photo = Photo.objects.filter(album=self.tuscany_album).first()
            self.assertIsInstance(photo, Photo)
            if photo:
                old_path = photo.image.path
                self.assertTrue(storage.exists(old_path))

                with self.subTest("Файл по старому адресу более не существует, но теперь существует по новому адресу"):
                    photo.album = self.langtang_album
                    new_path = move_photo_image(photo, photo.image.path)
                    self.assertFalse(storage.exists(old_path))
                    self.assertTrue(storage.exists(new_path))


class TestIsImage(SimpleTestCase):
    """Тесты утилиты для проверки на то, является ли файл изображением."""

    def test_true_image(self) -> None:
        """Изображение распознается как изображение."""
        jpeg_file = JpegFileProvider(FAKER).jpeg_file(storage=FS_STORAGE, raw=False)
        jpeg_file_path = FS_STORAGE.abspath(jpeg_file)
        self.assertTrue(storage.exists(jpeg_file_path))
        result = is_image(jpeg_file_path)
        self.assertTrue(result)

    def test_false_image(self) -> None:
        """Текстовый файл не распознается как изображение."""
        txt_file = TxtFileProvider(FAKER).txt_file(storage=FS_STORAGE, raw=False)
        txt_file_path = FS_STORAGE.abspath(txt_file)
        self.assertTrue(storage.exists(txt_file_path))
        result = is_image(txt_file_path)
        self.assertFalse(result)


class TestExifUtils(SimpleTestCase):
    """Тесты утилит для работы с EXIF."""

    @classmethod
    def setUpClass(cls) -> None:
        """Подготовка тестового изображения."""
        file_name = FAKER.file_name(extension="jpeg")
        cls.file_path = f"gallery/photos/{file_name}"
        jpeg_file = JpegFileProvider(FAKER).jpeg_file(raw=True)
        storage.save(name=cls.file_path, content=jpeg_file)
        return super().setUpClass()

    def test_read_write_exif(self) -> None:
        """Утилита для записи EXIF в изображение сохраняет данные EXIF в файл."""
        self.assertTrue(storage.exists(self.file_path))
        # Перед вызовом функции прочитать данные EXIF из изображения
        # и убедиться, что проверяемый атрибут не содержит значения.
        exif = read_exif(self.file_path)
        self.assertIsInstance(exif, ExifData)
        self.assertIsNone(exif.model)

        # Вызвать функцию, передав случайно сгенерированный набор данных.
        exif_data = ExifDataFactory.build()
        write_exif(self.file_path, exif_data)

        # После вызова функции повторно прочитать данные EXIF из изображения
        # и убедиться, что проверяемый атрибут содержит значение, которое
        # соответствует значению из сгенерированного набора данных.
        exif = read_exif(self.file_path)
        self.assertIsInstance(exif, ExifData)
        self.assertIsNotNone(exif.model)
        self.assertEqual(exif.model, exif_data.model)


class TestComputeDateTimeTaken(SimpleTestCase):
    """Тесты функции вычисления даты и времени съемки."""

    def test_with_exif_datetime_original(self) -> None:
        """Функция возвращает дату из EXIF DateTimeOriginal."""
        photo = MagicMock(spec=Photo)
        photo.image.name = "test.jpg"
        photo.exif = {"DateTimeOriginal": "2024:07:21 15:30:45"}

        file_time = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None) - timedelta(hours=1)

        with (
            patch("gallery.utils.storage.exists", return_value=True),
            patch("gallery.utils.storage.get_modified_time", return_value=file_time),
        ):
            result = compute_datetime_taken(photo)

        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 7)
        self.assertEqual(result.day, 21)
        self.assertEqual(result.hour, 15)
        self.assertEqual(result.minute, 30)

    def test_without_exif_fallback_to_file_time(self) -> None:
        """Функция использует время файла при отсутствии EXIF DateTimeOriginal."""
        photo = MagicMock(spec=Photo)
        photo.image.name = "test.jpg"
        photo.exif = {}

        file_time = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None) - timedelta(hours=1)

        with (
            patch("gallery.utils.storage.exists", return_value=True),
            patch(
                "gallery.utils.storage.get_modified_time",
                return_value=file_time,
            ),
        ):
            result = compute_datetime_taken(photo)

        self.assertIsInstance(result, datetime)
        self.assertEqual(result, file_time)

    def test_missing_file_returns_now(self) -> None:
        """Функция возвращает текущее время при отсутствии файла."""
        photo = MagicMock(spec=Photo)
        photo.image.name = "test.jpg"

        with patch("gallery.utils.storage.exists", return_value=False):
            result = compute_datetime_taken(photo)

        self.assertIsInstance(result, datetime)

    def test_empty_image_name_returns_now(self) -> None:
        """Функция возвращает текущее время при пустом имени файла."""
        photo = MagicMock(spec=Photo)
        photo.image.name = ""
        result = compute_datetime_taken(photo)
        self.assertIsInstance(result, datetime)

    def test_invalid_exif_datetime_fallback_to_file_time(self) -> None:
        """Функция использует время файла при невалидном формате EXIF DateTimeOriginal."""
        photo = MagicMock(spec=Photo)
        photo.image.name = "test.jpg"
        photo.exif = {"DateTimeOriginal": "invalid_format"}

        file_time = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None) - timedelta(hours=1)

        with (
            patch("gallery.utils.storage.exists", return_value=True),
            patch(
                "gallery.utils.storage.get_modified_time",
                return_value=file_time,
            ),
        ):
            result = compute_datetime_taken(photo)

        self.assertIsInstance(result, datetime)
        self.assertEqual(result, file_time)

    def test_timezone_aware_conversion_to_naive(self) -> None:
        """Функция преобразует timezone-aware datetime в naive."""
        photo = MagicMock(spec=Photo)
        photo.image.name = "test.jpg"
        photo.exif = {}

        # timezone-aware datetime
        file_time = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None) - timedelta(hours=1)

        with (
            patch("gallery.utils.storage.exists", return_value=True),
            patch(
                "gallery.utils.storage.get_modified_time",
                return_value=file_time,
            ),
            patch("gallery.utils.is_aware", return_value=True),
            patch(
                "gallery.utils.make_naive",
                side_effect=lambda x: x.replace(tzinfo=None),
            ) as mock_make_naive,
        ):
            result = compute_datetime_taken(photo)

        self.assertIsInstance(result, datetime)
        self.assertIsNone(result.tzinfo)
        mock_make_naive.assert_called_once()


class TestExifValueToJson(SimpleTestCase):
    """Тесты функции преобразования значений EXIF в JSON-совместимые типы."""

    def test_primitive_values_unchanged(self) -> None:
        """Примитивные типы передаются без изменений."""
        cases = [
            (400, 400, int),
            (2.8, 2.8, float),
            ("Canon", "Canon", str),
        ]
        for value, expected, expected_type in cases:
            with self.subTest(value=value):
                result = exif_value_to_json(value)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, expected_type)

    def test_ifd_rational_to_float(self) -> None:
        """IFDRational преобразуется в float."""
        for numerator, denominator in [(1, 250), (1, 125), (1, 60)]:
            with self.subTest(ratio=f"{numerator}/{denominator}"):
                result = exif_value_to_json(IFDRational(numerator, denominator))
                self.assertIsInstance(result, float)
                self.assertAlmostEqual(result, numerator / denominator, places=6)

    def test_bytes_returns_none(self) -> None:
        """Байтовые значения возвращают None (пропуск при сериализации)."""
        self.assertIsNone(exif_value_to_json(b"\x00\x01"))

    def test_tuple_converted_to_list(self) -> None:
        """Кортеж преобразуется в список."""
        result = exif_value_to_json((1, 2, 3))
        self.assertEqual(result, [1, 2, 3])
        self.assertIsInstance(result, list)
