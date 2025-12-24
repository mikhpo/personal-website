"""Тесты моделей галереи."""

import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING

from django.test import TestCase
from faker import Faker

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

        # Создать фотографии с помощью фабрик с заданными именами
        from gallery.factories import PhotoFactory

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
        photos_in_album: QuerySet[Photo] = self.tuscany_album.photo_set
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
            test_photos: QuerySet = test_album.photo_set.all()
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
            self.assertIn(album.slug, url)

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
        """Проверка получения даты и времени съемки фотографии."""
        first_photo = Photo.objects.first()
        self.assertIsInstance(first_photo, Photo)
        if first_photo:
            datetime_taken = first_photo.datetime_taken
            self.assertIsInstance(datetime_taken, datetime.datetime)

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
