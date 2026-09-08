"""Тесты аудита изменений моделей галереи через django-auditlog."""

from io import BytesIO
from typing import TYPE_CHECKING

from auditlog.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APITestCase

from gallery.factories import AlbumFactory, PhotoFactory, TagFactory
from gallery.models import Album, Photo, Tag

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

User = get_user_model()


class TestAlbumAuditLog(APITestCase):
    """Тесты аудита удаления альбома с каскадным удалением фотографий."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.album = AlbumFactory(name="Альбом для удаления", public=True)
        cls.photo1 = PhotoFactory(name="Фото 1", album=cls.album)
        cls.photo2 = PhotoFactory(name="Фото 2", album=cls.album)
        super().setUpTestData()

    def _entries(self, model: type, object_id: int) -> "QuerySet[LogEntry]":
        """Записи аудита для объекта модели."""
        content_type = ContentType.objects.get_for_model(model)
        return LogEntry.objects.filter(content_type=content_type, object_id=object_id)

    def test_album_delete_cascades_to_photos(self) -> None:
        """Удаление альбома фиксируется по альбому и каждой фотографии."""
        album_id, photo1_id, photo2_id = self.album.pk, self.photo1.pk, self.photo2.pk
        self.album.delete()
        self.assertIsNotNone(self._entries(Album, album_id).filter(action=LogEntry.Action.DELETE).first())
        self.assertIsNotNone(self._entries(Photo, photo1_id).filter(action=LogEntry.Action.DELETE).first())
        self.assertIsNotNone(self._entries(Photo, photo2_id).filter(action=LogEntry.Action.DELETE).first())


class TestPhotoAuditLog(APITestCase):
    """Тесты аудита фотографий и тегов."""

    def test_photo_create_logs_entry(self) -> None:
        """Создание фотографии фиксируется записью аудита."""
        photo = PhotoFactory(name="Новая фотография")
        content_type = ContentType.objects.get_for_model(Photo)
        entry = LogEntry.objects.get(content_type=content_type, object_id=photo.pk, action=LogEntry.Action.CREATE)
        self.assertIsNotNone(entry)

    def test_photo_delete_logs_entry(self) -> None:
        """Удаление фотографии фиксируется записью аудита."""
        photo = PhotoFactory(name="Фотография на удаление")
        photo_id = photo.pk
        photo.delete()
        content_type = ContentType.objects.get_for_model(Photo)
        entry = LogEntry.objects.get(content_type=content_type, object_id=photo_id, action=LogEntry.Action.DELETE)
        self.assertIsNotNone(entry)

    def test_tag_create_logs_entry(self) -> None:
        """Создание тега фиксируется записью аудита."""
        tag = TagFactory(name="Тег для аудита")
        content_type = ContentType.objects.get_for_model(Tag)
        entry = LogEntry.objects.get(content_type=content_type, object_id=tag.pk, action=LogEntry.Action.CREATE)
        self.assertIsNotNone(entry)


class TestUploadAuditLog(APITestCase):
    """Тесты аудита загрузки фотографий через API."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовка тестовых данных."""
        cls.staff_user = User.objects.create_user(username="staffuser", password="testpass123", is_staff=True)
        cls.album = AlbumFactory(name="Альбом для загрузки", public=True)
        cls.url = "/api/gallery/upload/"
        super().setUpTestData()

    def _create_test_image(self) -> SimpleUploadedFile:
        """Создать тестовое изображение для загрузки."""
        image_io = BytesIO()
        test_image = Image.new("RGB", (100, 100), color="red")
        test_image.save(image_io, format="JPEG")
        image_io.seek(0)
        return SimpleUploadedFile("audit_photo.jpg", image_io.read(), content_type="image/jpeg")

    def test_upload_logs_entry_with_actor(self) -> None:
        """Загрузка фотографии фиксируется записью аудита с автором загрузки."""
        self.client.force_authenticate(user=self.staff_user)
        data = {"album_id": self.album.pk, "photos": self._create_test_image()}
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, 201)
        photo_id = response.data["results"][0]["id"]
        content_type = ContentType.objects.get_for_model(Photo)
        entry = LogEntry.objects.get(content_type=content_type, object_id=photo_id, action=LogEntry.Action.CREATE)
        self.assertEqual(entry.actor, self.staff_user)
