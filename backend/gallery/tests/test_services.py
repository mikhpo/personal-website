"""Тесты сервиса пакетной загрузки фотографий в альбом."""

from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image, UnidentifiedImageError

from gallery.factories import AlbumFactory
from gallery.models import Album, Photo
from gallery.services import upload_error_message, upload_photos_to_album


class TestUploadPhotosToAlbum(TestCase):
    """Тесты пакетной загрузки фотографий в альбом."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные для выполнения тестов."""
        cls.album: Album = AlbumFactory(name="Тестовый альбом")
        return super().setUpTestData()

    def _create_test_image(self, filename: str = "test_image.jpg", color: str = "red") -> SimpleUploadedFile:
        """Создать тестовое изображение для загрузки."""
        image_io = BytesIO()
        image = Image.new("RGB", (100, 100), color=color)
        image.save(image_io, format="JPEG")
        image_io.seek(0)
        return SimpleUploadedFile(filename, image_io.read(), content_type="image/jpeg")

    def _create_invalid_file(self, filename: str = "invalid_file.jpg") -> SimpleUploadedFile:
        """Создать невалидный файл (не изображение) для загрузки."""
        return SimpleUploadedFile(filename, b"Not an image", content_type="image/jpeg")

    def test_valid_image_creates_photo(self) -> None:
        """Валидный файл создает фотографию в указанном альбоме."""
        results = upload_photos_to_album(self.album, [self._create_test_image()])

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertIsNone(results[0].error)
        self.assertEqual(results[0].filename, "test_image.jpg")

        photo = results[0].photo
        assert photo is not None
        self.assertEqual(photo.album, self.album)
        self.assertEqual(photo.name, "test_image")
        self.assertTrue(photo.image.name.startswith(f"gallery/albums/{self.album.pk}/photos/"))
        self.assertTrue(photo.image.storage.exists(photo.image.name))

    def test_invalid_file_not_created(self) -> None:
        """Невалидный файл не создает фотографию и дает результат с ошибкой."""
        results = upload_photos_to_album(self.album, [self._create_invalid_file()])

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)
        self.assertIsNone(results[0].photo)
        self.assertEqual(results[0].filename, "invalid_file.jpg")
        self.assertIsInstance(results[0].error, UnidentifiedImageError)
        self.assertFalse(Photo.objects.filter(album=self.album).exists())

    def test_mixed_batch_creates_only_valid(self) -> None:
        """В альбоме из валидных и невалидных файлов создаются только валидные фотографии."""
        files = [
            self._create_test_image("valid_1.jpg", "red"),
            self._create_invalid_file("invalid_1.jpg"),
            self._create_test_image("valid_2.jpg", "blue"),
        ]

        results = upload_photos_to_album(self.album, files)

        self.assertEqual([result.success for result in results], [True, False, True])
        self.assertEqual(Photo.objects.filter(album=self.album).count(), 2)
        self.assertEqual(Photo.objects.filter(name="invalid_1").count(), 0)

    def test_empty_files_list_gives_empty_results(self) -> None:
        """Пустой список файлов дает пустой список результатов."""
        self.assertEqual(upload_photos_to_album(self.album, []), [])

    def test_error_message_for_not_image(self) -> None:
        """Сообщение об ошибке для невалидного файла содержит имя файла."""
        result = upload_photos_to_album(self.album, [self._create_invalid_file("bad.jpg")])[0]

        message = upload_error_message(result, self.album)
        self.assertEqual(message, 'Загруженный файл "bad.jpg" не является изображением')
