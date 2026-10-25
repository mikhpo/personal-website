"""Тесты сериализаторов галереи."""

import datetime

from django.test import TestCase

from gallery.factories import AlbumFactory, PhotoFactory
from gallery.models import Photo
from gallery.serializers import AlbumDetailSerializer, PhotoDetailSerializer, PhotoSerializer


class TestPhotoSerializer(TestCase):
    """Тесты для PhotoSerializer."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.album = AlbumFactory()
        cls.photo = PhotoFactory(album=cls.album, public=True)
        super().setUpTestData()

    def test_photo_serializer_contains_album_name(self) -> None:
        """Сериализатор фотографии возвращает название альбома."""
        data = PhotoSerializer(self.photo).data
        self.assertEqual(data["album"], self.album.pk)
        self.assertEqual(data["album_name"], self.album.name)

    def test_detail_serializer_contains_neighbor_ids(self) -> None:
        """Детальный сериализатор возвращает id соседей фотографии по альбому."""
        other = PhotoFactory(album=self.album, public=True)
        # taken_at фиксируем через update(): фабрика задает случайные даты,
        # а Photo.save() перезаписывает поле из EXIF при создании
        taken_at = datetime.datetime(2024, 1, 1, 10, 0, tzinfo=datetime.timezone.utc)
        other_taken_at = datetime.datetime(2024, 1, 1, 11, 0, tzinfo=datetime.timezone.utc)
        Photo.objects.filter(pk=self.photo.pk).update(taken_at=taken_at)
        Photo.objects.filter(pk=other.pk).update(taken_at=other_taken_at)
        self.photo.refresh_from_db()

        data = PhotoDetailSerializer(self.photo).data
        self.assertIn("previous_id", data)
        self.assertIn("next_id", data)
        self.assertEqual(data["previous_id"], None)
        self.assertEqual(data["next_id"], other.pk)

    def test_list_serializer_has_no_neighbor_ids(self) -> None:
        """Базовый сериализатор не содержит полей соседей: они есть только в детальном."""
        data = PhotoSerializer(self.photo).data
        self.assertNotIn("previous_id", data)
        self.assertNotIn("next_id", data)

    def test_detail_serializer_many_keeps_neighbors_per_object(self) -> None:
        """Детальный сериализатор при many=True вычисляет соседей для каждой фотографии отдельно."""
        first, second, third = (
            PhotoFactory(album=self.album, public=True),
            PhotoFactory(album=self.album, public=True),
            PhotoFactory(album=self.album, public=True),
        )
        # taken_at фиксируем через update(): фабрика задает случайные даты,
        # а Photo.save() перезаписывает поле из EXIF при создании
        for offset, photo in enumerate([self.photo, first, second, third]):
            taken_at = datetime.datetime(2024, 1, 1, 10 + offset, 0, tzinfo=datetime.timezone.utc)
            Photo.objects.filter(pk=photo.pk).update(taken_at=taken_at)
            photo.refresh_from_db()

        data = PhotoDetailSerializer([self.photo, first], many=True).data
        self.assertIsNone(data[0]["previous_id"])
        self.assertEqual(data[0]["next_id"], first.pk)
        self.assertEqual(data[1]["previous_id"], self.photo.pk)
        self.assertEqual(data[1]["next_id"], second.pk)


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
