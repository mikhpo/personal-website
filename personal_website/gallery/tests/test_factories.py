"""Тесты фабрик для создания объектов галереи."""

from typing import TYPE_CHECKING

from django.test import SimpleTestCase, TestCase

from gallery.factories import AlbumFactory, ExifDataFactory, PhotoFactory, TagFactory
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


class TestExifDataFactory(SimpleTestCase):
    """Тест фабрики данных EXIF."""

    def test_exif_data_factory(self) -> None:
        """Фабрика создает экземпляр модели данных Exif."""
        exif_data = ExifDataFactory()
        self.assertIsInstance(exif_data, ExifData)
