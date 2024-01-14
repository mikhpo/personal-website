import os
from pathlib import Path

from django.test import TestCase

from gallery.models import Album, Photo
from gallery.utils import move_photo_image, photo_image_upload_full_path, photo_image_upload_path
from personal_website.utils import list_file_paths


class GalleryUtilsTests(TestCase):
    """
    Тесты утилит приложения галереи.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        # Создать альбомы.
        cls.tuscany_album = Album.objects.create(
            name="Тоскана",
            description="Фотографии из путешествия по Тоскане осенью 2013 года",
            slug="tuscany",
        )
        cls.langtang_album = Album.objects.create(
            name="Лангтанг",
            description="Фотографии из путешествия по Лангтангу весной 2014 года",
        )

        # Создать фотографии в базе данных из картинок в директории проекта.
        test_dir = os.getenv("TEMP_ROOT")
        test_images_dir = os.path.join(test_dir, "gallery", "photos")
        images = list_file_paths(test_images_dir)
        for image in images:
            if "Tuscany" in image:
                album = cls.tuscany_album
            elif "Langtang" in image:
                album = cls.langtang_album
            else:
                raise Exception("Нужно создать новый тестовый альбом")
            Photo.objects.create(image=image, album=album)

    def test_photo_image_upload_path(self):
        """
        Проверка функции получения относительного пути загрузки файла изображения.
        """
        first_photo = Photo.objects.first()
        relative_path = photo_image_upload_path(first_photo, "test.jpg")
        self.assertIsInstance(relative_path, str)
        absolute = Path(relative_path).is_absolute()
        self.assertFalse(absolute)

    def test_photo_image_upload_full_path(self):
        """
        Проверка функции получения абсолютного пути загрузки файла изображения.
        """
        first_photo = Photo.objects.first()
        relative_path = photo_image_upload_full_path(first_photo, "test.jpg")
        absolute = Path(relative_path).is_absolute()
        self.assertIsInstance(relative_path, str)
        self.assertTrue(absolute)

    def test_move_photo_image(self):
        """
        Проверка функции перемещения фотографии по новому адресу.
        """
        with self.subTest("Файл по старому адресу существует"):
            photo = Photo.objects.filter(album=self.tuscany_album).first()
            old_path = photo.image.path
            self.assertTrue(Path(old_path).exists())

        with self.subTest("Файл по старому адресу более не существует," " но теперь существует по новому адресу"):
            photo.album = self.langtang_album
            new_path = move_photo_image(photo, photo.image.path)
            self.assertFalse(Path(old_path).exists())
            self.assertTrue(Path(new_path).exists())
