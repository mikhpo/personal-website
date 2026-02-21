"""Тесты фабрик для создания объектов галереи."""

from typing import TYPE_CHECKING

from django.test import SimpleTestCase, TestCase
from PIL import Image as pImage

from gallery.factories import AlbumFactory, ExifDataFactory, PhotoFactory, TagFactory, generate_image_with_exif
from gallery.models import Album, Photo, Tag
from gallery.schemas import ExifData

if TYPE_CHECKING:
    from django.db.models import QuerySet


class TestTagFactory(TestCase):
    """Тесты фабрики для создания тэгов."""

    def test_tag_factory_instance(self) -> None:
        """Фабрика тэгов возвращает объекта тэга."""
        tag = TagFactory()
        self.assertIsInstance(tag, Tag)


class TestAlbumFactory(TestCase):
    """Тесты фабрики для создания альбомов."""

    def test_album_factory_instance(self) -> None:
        """Фабрика альбомов возвращет объект альбома."""
        album = AlbumFactory()
        self.assertIsInstance(album, Album)

    def test_album_factory_create_tags(self) -> None:
        """Связанные тэги создаются."""
        tags = tuple(TagFactory() for _ in range(3))
        album = AlbumFactory.create(tags=tags)
        tags_qs: QuerySet[Tag] = album.tags.all()
        self.assertTrue(tags_qs.exists())


class TestPhotoFactory(TestCase):
    """Тесты фабрики для создания фотографий."""

    def test_photo_factory_instance(self) -> None:
        """Фабрика фотографии возвращает объект фотографии."""
        photo = PhotoFactory()
        self.assertIsInstance(photo, Photo)

    def test_photo_factory_create_tags(self) -> None:
        """Связанные тэги создаются."""
        tags = tuple(TagFactory() for _ in range(3))
        photo = PhotoFactory.create(tags=tags)
        tags_qs: QuerySet[Tag] = photo.tags.all()
        self.assertTrue(tags_qs.exists())

    def test_photo_factory_creates_album(self) -> None:
        """Фабрика создает связанный объект альбома."""
        photo = PhotoFactory()
        self.assertIsNotNone(photo.album)
        self.assertIsInstance(photo.album, Album)

    def test_photo_factory_image_has_exif(self) -> None:
        """Сгенерированное изображение содержит EXIF данные."""
        photo = PhotoFactory.create()
        with pImage.open(photo.image) as img:
            exif = img.getexif()
            exif_dict = dict(exif.items())
            self.assertIn(271, exif_dict)  # Make
            self.assertIn(272, exif_dict)  # Model
            self.assertIn(33434, exif_dict)  # FNumber
            self.assertIn(34855, exif_dict)  # ISOSpeedRatings
            self.assertIn(37386, exif_dict)  # FocalLength
            self.assertIn(36867, exif_dict)  # DateTimeOriginal


class TestExifDataFactory(SimpleTestCase):
    """Тест фабрики данных EXIF."""

    def test_exif_data_factory(self) -> None:
        """Фабрика создает экземпляр модели данных Exif."""
        exif_data = ExifDataFactory()
        self.assertIsInstance(exif_data, ExifData)


class TestGenerateImageWithExif(SimpleTestCase):
    """Тесты функции генерации изображений с EXIF данными."""

    def test_generate_image_with_exif_auto(self) -> None:
        """Функция генерирует изображение со случайными EXIF данными."""
        image_file = generate_image_with_exif()
        with pImage.open(image_file) as img:
            exif = dict(img.getexif().items())
            self.assertIn(271, exif)  # Make
            self.assertIn(272, exif)  # Model

    def test_generate_image_with_exif_custom(self) -> None:
        """Функция генерирует изображение с переданными EXIF данными."""
        custom_exif = ExifDataFactory.build(make="Nikon", model="D850")
        image_file = generate_image_with_exif(custom_exif)
        with pImage.open(image_file) as img:
            exif = dict(img.getexif().items())
            self.assertEqual(exif.get(271), "Nikon")
            self.assertEqual(exif.get(272), "D850")
