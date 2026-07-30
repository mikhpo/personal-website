"""Тесты моделей галереи."""

import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING
from unittest.mock import patch

from django.test import TestCase
from faker import Faker

from gallery.factories import PhotoFactory
from gallery.models import Album, Photo, Tag, photo_image_upload_path
from personal_website.storages import FakerFileStorageAdapter, StorageType, select_storage

if TYPE_CHECKING:
    from django.db.models import QuerySet

storage: StorageType = select_storage()

FAKER = Faker()
FS_STORAGE = FakerFileStorageAdapter(rel_path="gallery/photos/test_models")


class GalleryModelsTests(TestCase):
    """Тестирование моделей галереи. Фотографии заранее сохранены в директории /media/ проекта."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Метод применяется один раз перед выполнением тестов класса."""
        super().setUpTestData()

        # Создать теги.
        for tag in ["Путешествия", "Италия", "Тоскана", "Непал", "Лангтанг"]:
            Tag.objects.create(name=tag)

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

        # Создать 3 фотографии для альбома "Тоскана" с именами, содержащими "Tuscany"
        for i in range(3):
            PhotoFactory.create(
                album=cls.tuscany_album,
                name=f"Tuscany Photo {i + 1}",
            )

        # Создать 2 фотографии для альбома "Лангтанг" с именами, содержащими "Langtang"
        for i in range(2):
            PhotoFactory.create(
                album=cls.langtang_album,
                name=f"Langtang Photo {i + 1}",
            )

    def test_objects_created(self) -> None:
        """Проверить, что все объекты для тестирования созданы."""
        self.assertEqual(Tag.objects.all().count(), 5)
        self.assertEqual(Album.objects.all().count(), 2)
        self.assertEqual(Photo.objects.all().count(), 5)

    def test_photo_fields_auto_save(self) -> None:
        """Проверяет, что некоторые атрибуты фотографий определяются автоматически."""
        photos = Photo.objects.all()
        fields = ["name", "slug", "uploaded_at", "modified_at", "public"]
        for photo in photos:
            for field in fields:
                value = getattr(photo, field)
                self.assertNotEqual(value, "")

    def test_slugs_auto_created(self) -> None:
        """Проверить, что слаги объектов автоматически создаются."""
        # Проверить, что слаги тэгов автоматически создаются с применением транслита.
        tag = Tag.objects.get(name="Италия")
        self.assertEqual(tag.slug, "italiya")

        # Убедиться, что слаги альбомов автоматически создаются с применением транслита, если слаг не был задан вручную.
        # Если название альбома поменялось, то слаг должен измениться автоматически.
        langtang_album = Album.objects.get(name="Лангтанг")
        tuscany_album = Album.objects.get(name="Тоскана")
        self.assertEqual(langtang_album.slug, "langtang")
        self.assertEqual(tuscany_album.slug, "tuscany")

        # Убедиться, что слаги фотографий создаются из названий с переводом
        # в нижний регистр и заменой специальных символов.
        photo = Photo.objects.filter(name__contains="Tuscany").first()
        self.assertIsNotNone(photo)
        if photo:
            self.assertIsNotNone(photo.slug)

    def test_photo_exif(self) -> None:
        """Проверить, что данные EXIF считываются корректно."""
        photo = Photo.objects.first()
        self.assertIsNotNone(photo)
        if photo:
            self.assertIsNotNone(photo.exif)

    def test_photo_camera(self) -> None:
        """Проверить, что данные EXIF считываются корректно."""
        photo = Photo.objects.first()
        self.assertIsNotNone(photo)
        if photo:
            self.assertIsNotNone(photo.camera)

    def test_photo_album_relations(self) -> None:
        """Проверить отношения между моделью фотографии и моделью альбома."""
        # Отобрать фотографии для добавления в альбомы.
        tuscany_photos = Photo.objects.filter(name__contains="Tuscany")

        # Проверить количество фотографий в тосканском альбоме.
        photos_in_album: QuerySet[Photo] = self.tuscany_album.photos
        self.assertEqual(photos_in_album.count(), 3)
        self.assertEqual(self.tuscany_album.photos_count, 3)

        # Удалить последнюю тосканскую фотографию и проверить, что в тосканском альбоме осталось две фотографии.
        last_tuscany_photo = tuscany_photos.last()
        self.assertIsNotNone(last_tuscany_photo)
        if last_tuscany_photo:
            last_tuscany_photo.delete()
        photos_in_album.all()
        self.assertEqual(photos_in_album.count(), 2)
        self.assertEqual(self.tuscany_album.photos_count, 2)

        # Сделать одну из фотографий непубличной и убедиться,
        # что счетчик публичных фотографий меньше счетчика фотографий.
        photo = photos_in_album.first()
        self.assertIsNotNone(photo)
        if photo:
            photo.public = False
            photo.save()
        self.assertEqual(self.tuscany_album.public_photos_count, 1)

        # Удалить альбом и проверить, что все фотографии из него были также удалены.
        self.tuscany_album.delete()
        tuscany_photos.all()
        self.assertFalse(tuscany_photos.exists())

    def test_tags_relations(self) -> None:
        """Проверить отношения модели тэга с моделями фотографии и альбома."""
        # Отобрать объекты из тестовой базы данных для модуля.
        tuscany_photos = Photo.objects.filter(name__contains="Tuscany")
        langtang_photos = Photo.objects.filter(name__contains="Langtang")
        all_photos = Photo.objects.all()
        travel_tag = Tag.objects.get(name="Путешествия")
        italy_tag = Tag.objects.get(name="Италия")
        tuscany_tag = Tag.objects.get(name="Тоскана")
        nepal_tag = Tag.objects.get(name="Непал")
        langtang_tag = Tag.objects.get(name="Лангтанг")
        all_tags = Tag.objects.all()

        # Проверить, что сейчас ни один тэг не связан ни с одной фотографией и ни с одним альбомом.
        for tag in all_tags:
            self.assertEqual(tag.tag_albums.count(), 0)
            self.assertEqual(tag.tag_photos.count(), 0)

        # Для трех тосканских фотографий добавить тосканский тэг,
        # проверить количество тэгов у каждой фотографии и общее количество фотографий у тэга.
        for photo in tuscany_photos:
            photo.tags.add(tuscany_tag)
            self.assertEqual(photo.tags.count(), 1)
        self.assertEqual(tuscany_tag.tag_photos.count(), 3)

        # Для двух лангтангских фотографий добавить лангтангский тэг,
        # проверить количество тэгов у каждой фотографии и общее количество фотографий у тэга.
        for photo in langtang_photos:
            photo.tags.add(langtang_tag)
            self.assertEqual(photo.tags.count(), 1)
        self.assertEqual(langtang_tag.tag_photos.count(), 2)

        # Привязать итальянский тэг к тосканским фотографиям,
        # проверить общее количество фотографий у тэга и количество тэгов у каждой фотографии из серии.
        italy_tag.tag_photos.set(tuscany_photos)
        self.assertEqual(italy_tag.tag_photos.count(), 3)
        for photo in tuscany_photos:
            self.assertEqual(photo.tags.count(), 2)

        # Привязать непальский тэг к лангтангским фотографиям,
        # проверить общее количество фотографий у тэга и количество тэгов у каждой фотографии из серии.
        nepal_tag.tag_photos.add(*langtang_photos)
        self.assertEqual(nepal_tag.tag_photos.count(), 2)
        for photo in langtang_photos:
            self.assertEqual(photo.tags.count(), 2)

        # Добавить общий тэг ко всем фотографиям, проверить общее количество
        # фотографий у тэга и количество тэгов у каждой фотографии.
        travel_tag.tag_photos.set(all_photos)
        self.assertEqual(travel_tag.tag_photos.count(), 5)
        for photo in all_photos:
            self.assertEqual(photo.tags.count(), 3)

        # Удалить общий тэг и проверить, что количество тэгов у каждой фотографии уменьшилось.
        travel_tag.delete()
        self.assertFalse(Tag.objects.filter(name="Путешествия").exists())
        for photo in all_photos:
            self.assertEqual(photo.tags.count(), 2)

        # Удалить последнюю тосканскую фотографию и убедиться, что уменьшилось количество фотографий у тосканского тэга.
        last_tuscany_photo = tuscany_photos.last()
        self.assertIsNotNone(last_tuscany_photo)
        if last_tuscany_photo:
            last_tuscany_photo.delete()
        self.assertEqual(tuscany_tag.tag_photos.count(), 2)

        # Удалить непальский тэг у последней лангтангской фотографии и убедиться,
        # что количество тэгов у фотографии уменьшилось.
        last_langtang_photo = langtang_photos.last()
        self.assertIsNotNone(last_langtang_photo)
        if last_langtang_photo:
            self.assertEqual(last_langtang_photo.tags.count(), 2)
            last_langtang_photo.tags.remove(nepal_tag)
            self.assertEqual(last_langtang_photo.tags.count(), 1)

        # Добавить тэги албомам разными способами и проверить количество тэгов у альбомов и количество альбомов у тэгов.
        tuscany_tag.tag_albums.add(self.tuscany_album)
        self.assertEqual(tuscany_tag.tag_albums.count(), 1)
        self.assertEqual(self.tuscany_album.tags.count(), 1)
        self.langtang_album.tags.add(langtang_tag)
        self.assertEqual(langtang_tag.tag_albums.count(), 1)
        self.assertEqual(self.langtang_album.tags.count(), 1)

        # Удалить у альбома тэг и проверить, что у альбома не осталось тэгов.
        self.langtang_album.tags.remove(langtang_tag)
        self.assertEqual(langtang_tag.tag_albums.count(), 0)

    def test_album_remains_when_cover_deleted(self) -> None:
        """Проверить, что при удалении фотографии, служащей обложкой, альбом не удаляется."""
        # Установить обложку для альбома из фотографии в этом альбоме.
        # Убедиться, что обложка установлена и является экземпляром класса фотографии.
        test_album = Album.objects.first()
        self.assertIsNotNone(test_album)
        if test_album:
            test_photos: QuerySet = test_album.photos.all()
            test_album.cover = test_photos.first()
            test_album.save()
            self.assertIsNotNone(test_album.cover)
            self.assertIsInstance(test_album.cover, Photo)

            # Удалить фотографию, служащую обложкой и перезагрузить из БД атрибуты альбома.
            # Убедиться, что альбом сохранен, а обложка не установлена.
            cover_photo: Photo = test_album.cover  # type: ignore[assignment]
            cover_photo.delete()
            test_album.refresh_from_db()
            self.assertEqual(test_album.cover, None)
            self.assertNotIsInstance(test_album.cover, Photo)

    def test_photo_get_absolute_url(self) -> None:
        """Проверить корректность определения абсолютной ссылки для просмотра фотографии."""
        photo = Photo.objects.first()
        self.assertIsInstance(photo, Photo)
        if photo:
            url = photo.get_absolute_url()
            response = self.client.get(url)
            status_code = response.status_code
            self.assertEqual(status_code, HTTPStatus.OK)

    def test_album_get_absolute_url(self) -> None:
        """Проверить корректность определения абсолютной ссылки для просмотра альбома."""
        album = Album.objects.first()
        self.assertIsInstance(album, Album)
        if album:
            url = album.get_absolute_url()
            self.assertIsInstance(url, str)
            self.assertIn(str(album.pk), url)

    def test_tag_get_absolute_url(self) -> None:
        """Проверить корректность определения абсолютной ссылки для просмотра тега."""
        tag = Tag.objects.first()
        self.assertIsInstance(tag, Tag)
        if tag:
            url = tag.get_absolute_url()
            response = self.client.get(url)
            status_code = response.status_code
            self.assertEqual(status_code, HTTPStatus.OK)

    def test_datetime_taken(self) -> None:
        """Проверка поля даты и времени съемки фотографии."""
        first_photo = Photo.objects.first()
        self.assertIsInstance(first_photo, Photo)
        if first_photo:
            self.assertIsNotNone(first_photo.taken_at)
            self.assertIsInstance(first_photo.taken_at, datetime.datetime)

    def test_should_update_taken_at_new_instance(self) -> None:
        """Метод should_update_taken_at возвращает True для нового экземпляра."""
        photo = Photo()
        self.assertTrue(photo.should_update_taken_at())

    def test_should_update_taken_at_image_changed(self) -> None:
        """Метод should_update_taken_at возвращает True при изменении изображения."""
        photo1 = PhotoFactory(album=self.tuscany_album)
        photo2 = PhotoFactory(album=self.tuscany_album)

        # Имитация изменения изображения
        photo2.image.name = photo1.image.name
        self.assertTrue(photo2.should_update_taken_at())

    def test_should_update_taken_at_same_image(self) -> None:
        """Метод should_update_taken_at возвращает False при том же изображении."""
        photo = PhotoFactory(album=self.tuscany_album)
        original_pk = photo.pk
        photo_from_db = Photo.objects.get(pk=original_pk)
        self.assertFalse(photo_from_db.should_update_taken_at())

    def test_photo_album_changed(self) -> None:
        """Путь фотографии изменяется после изменения альбома фотографии."""
        # Файл по изначальному адресу существует.
        photo = Photo.objects.filter(album=self.tuscany_album).last()
        self.assertIsInstance(photo, Photo)
        if photo:
            old_path = photo.image.path
            old_path_exists = storage.exists(old_path)
            self.assertTrue(old_path_exists)

            # Изменить альбом и сохранить фотографию.
            old_relative_path = photo.image.name
            file_name = storage.name(old_relative_path)
            photo.album = self.langtang_album
            photo.save()

            # Адрес файла был изменен корректно.
            new_name_is_absolute = storage.is_absolute(photo.image.name)
            new_path_exists = storage.exists(photo.image.path)
            upload_path = photo_image_upload_path(photo, file_name)
            self.assertFalse(new_name_is_absolute)
            self.assertNotEqual(old_relative_path, photo.image.name)
            self.assertEqual(photo.image.name, upload_path)
            self.assertTrue(new_path_exists)

    def test_photo_exif_field_populated(self) -> None:
        """Поле exif заполняется при сохранении фотографии."""
        photo = Photo.objects.first()
        self.assertIsInstance(photo, Photo)
        if photo:
            self.assertIsInstance(photo.exif, dict)
            self.assertTrue(photo.exif, "Поле exif должно быть заполнено после save()")
            self.assertIn("Make", photo.exif)
            self.assertIn("Model", photo.exif)

    def test_photo_exif_persisted_in_db(self) -> None:
        """Поле exif сохраняется в БД и доступно после перезагрузки объекта."""
        photo = Photo.objects.first()
        self.assertIsInstance(photo, Photo)
        if photo:
            photo.refresh_from_db()
            self.assertTrue(photo.exif)
            self.assertIn("Make", photo.exif)

    def test_photo_exif_reads_without_storage_access(self) -> None:
        """Производные свойства читаются из поля exif без обращения к хранилищу."""
        photo = Photo.objects.first()
        self.assertIsInstance(photo, Photo)
        if photo:
            photo.refresh_from_db()
            # При наличии exif в БД обращение к read_bytes не выполняется.
            with patch.object(
                photo.image.storage,
                "read_bytes",
                side_effect=AssertionError("read_bytes не должен вызываться"),
            ):
                _ = photo.camera
                _ = photo.lens_model
                _ = photo.aperture
                _ = photo.exposure
                _ = photo.iso
                _ = photo.focal_length

    def test_photo_exif_not_recomputed_when_image_unchanged(self) -> None:
        """При повторном сохранении без изменения изображения поле exif не пересчитывается."""
        photo = Photo.objects.first()
        self.assertIsInstance(photo, Photo)
        if photo:
            original_exif = dict(photo.exif)
            photo.name = "Изменённое название"
            photo.save()
            photo.refresh_from_db()
            self.assertEqual(photo.exif, original_exif)

    def test_photo_exif_derived_from_json_values(self) -> None:
        """Производные свойства корректно вычисляются из JSON-значений поля exif."""
        photo = Photo.objects.first()
        self.assertIsInstance(photo, Photo)
        if photo:
            test_cases = [
                ("ExposureTime", 1 / 250, lambda p: p.exposure, "1/250"),
                ("ExposureTime", 60.0, lambda p: p.exposure, "60"),
                ("FNumber", 4.0, lambda p: p.aperture, "F/4"),
                ("FNumber", 2.8, lambda p: p.aperture, "F/2.8"),
                ("ISOSpeedRatings", 400, lambda p: p.iso, 400),
                ("FocalLength", 50, lambda p: p.focal_length, 50),
            ]
            for key, value, getter, expected in test_cases:
                with self.subTest(key=key, value=value):
                    photo.exif = {key: value}
                    # Сбросить кэшированные свойства.
                    for prop in ("exposure", "aperture", "iso", "focal_length"):
                        photo.__dict__.pop(prop, None)
                    self.assertEqual(getter(photo), expected)

    def test_photo_exif_none_handled_gracefully(self) -> None:
        """Производные свойства возвращают значения по умолчанию при пустом exif."""
        photo = Photo.objects.first()
        self.assertIsInstance(photo, Photo)
        if photo:
            photo.exif = None
            # Сбросить все кэшированные свойства.
            for prop in (
                "camera_manufacturer",
                "camera_model",
                "camera",
                "lens_model",
                "aperture",
                "exposure",
                "iso",
                "focal_length",
            ):
                photo.__dict__.pop(prop, None)

            with self.subTest(prop="camera"):
                self.assertEqual(photo.camera, "")
            with self.subTest(prop="lens_model"):
                self.assertEqual(photo.lens_model, "")
            with self.subTest(prop="aperture"):
                self.assertIsNone(photo.aperture)
            with self.subTest(prop="exposure"):
                self.assertEqual(photo.exposure, "")
            with self.subTest(prop="iso"):
                self.assertIsNone(photo.iso)
            with self.subTest(prop="focal_length"):
                self.assertIsNone(photo.focal_length)
