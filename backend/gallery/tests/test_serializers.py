"""Тесты сериализаторов галереи."""

from django.test import TestCase

from gallery.factories import AlbumFactory, PhotoFactory
from gallery.serializers import AlbumDetailSerializer


class TestAlbumDetailSerializer(TestCase):
    """Тесты для AlbumDetailSerializer."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.album = AlbumFactory()
        cls.photo1 = PhotoFactory(album=cls.album, public=True)
        cls.photo2 = PhotoFactory(album=cls.album, public=True)
        super().setUpTestData()

    def test_album_serializer_contains_nested_photos(self) -> None:
        """Сериализатор альбома возвращает вложенные фотографии."""
        data = AlbumDetailSerializer(self.album).data
        self.assertIn("photos", data)
        self.assertEqual(len(data["photos"]), 2)
