"""Тесты вспомогательных утилит галереи."""

from pathlib import Path

from django.test import SimpleTestCase, TestCase
from faker import Faker
from faker_file.providers.jpeg_file import JpegFileProvider  # type:ignore[import-untyped]
from faker_file.providers.txt_file import TxtFileProvider  # type:ignore[import-untyped]

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
        exif_data = ExifDataFactory()
        write_exif(self.file_path, exif_data)

        # После вызова функции повторно прочитать данные EXIF из изображения
        # и убедиться, что проверяемый атрибут содержит значение, которое
        # соответствует значению из сгенерированного набора данных.
        exif = read_exif(self.file_path)
        self.assertIsInstance(exif, ExifData)
        self.assertIsNotNone(exif.model)
        self.assertEqual(exif.model, exif_data.model)
