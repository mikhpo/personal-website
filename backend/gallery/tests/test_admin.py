"""Тесты представлений галереи в административной панели Django."""

from http import HTTPStatus
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import resolve, reverse

from gallery.apps import GalleryConfig
from gallery.factories import AlbumFactory, PhotoFactory
from gallery.models import Album, Photo, Tag
from personal_website.storages import StorageType, select_storage
from personal_website.utils import list_file_paths

ADMIN_URL = "/admin/"
storage: StorageType = select_storage()


class GalleryAdminTests(TestCase):
    """Тестирование функциональности раздела галереи в административном интерфейсе Django."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Подготовить тестовые данные для выполнения тестов."""
        cls.superuser: User = User.objects.create_superuser(username="testadmin", password="12345")
        cls.user: User = User.objects.create_user(username="testuser", password="12345")
        cls.album: Album = AlbumFactory(name="Тестовый альбом")
        test_images_dir = "gallery/photos"
        cls.image_path = list_file_paths(test_images_dir)[0]
        return super().setUpTestData()

    def setUp(self) -> None:
        """Авторизоваться под пользователем-администратором."""
        self.client.login(username="testadmin", password="12345")
        return super().setUp()

    def _uploaded_image(self, filename: str) -> SimpleUploadedFile:
        """Создать загружаемый файл из тестового изображения."""
        return SimpleUploadedFile(name=filename, content=storage.read_bytes(self.image_path))

    def test_gallery_admin_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображется раздел галереи."""
        app_verbose_name = GalleryConfig.verbose_name
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, app_verbose_name)
        url = ADMIN_URL + "gallery/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for action in ["Добавить", "Изменить"]:
            self.assertContains(response, action)

    def test_photo_admin_list_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображается модель фотографии."""
        url = ADMIN_URL + "gallery/photo/"
        photos_verbose_name = Photo._meta.verbose_name_plural  # noqa: SLF001
        self.assertIsNotNone(photos_verbose_name)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, str(photos_verbose_name))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_photo_change_page_rendered(self) -> None:
        """Проверяет корректность отображения страницы изменения фотографии."""
        with self.subTest("Получение страницы детального просмотра и изменения"):
            album = AlbumFactory(name="Test album")
            photo = PhotoFactory(name="Test photo", album=album, image=None)
            slug = "test-photo"
            url = ADMIN_URL + f"gallery/photo/{photo.pk}/change/"
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(photo.slug, slug)
            self.assertIsNone(photo.image.name)

        with self.subTest("Отправка данных для изменения объекта"):
            new_slug = "new-slug"
            file_content = storage.read_bytes(self.image_path)
            file_name = Path(self.image_path).name
            data = {
                "image": SimpleUploadedFile(file_name, file_content),
                "name": photo.name,
                "album": album.pk,
                "slug": new_slug,
            }
            response = self.client.post(url, data)
            photo.refresh_from_db()
            self.assertEqual(photo.slug, new_slug)
            self.assertIsNotNone(photo.image.name)

    def test_album_admin_list_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображается модель альбома."""
        albums_verbose_name = Album._meta.verbose_name_plural  # noqa: SLF001
        self.assertIsNotNone(albums_verbose_name)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, str(albums_verbose_name))
        url = ADMIN_URL + "gallery/album/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tag_admin_list_page_displayed(self) -> None:
        """Проверяет, что в административной панели отображается модель тэга."""
        tags_verbose_name = Tag._meta.verbose_name_plural  # noqa: SLF001
        self.assertIsNotNone(tags_verbose_name)
        response = self.client.get(ADMIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, str(tags_verbose_name))
        url = ADMIN_URL + "gallery/tag/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_photo_add_via_admin(self) -> None:
        """Проверяет успешность добавления фотографии через административную панель."""
        # Создать альбом, в который будет добавляться фотография.
        album = AlbumFactory(name="Тестовый альбом")
        photo_name = storage.stem(self.image_path)

        # Ссылка на форму добавления фотографии в административной панели.
        url = ADMIN_URL + "gallery/photo/add/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Загрузить фотографию, проверить статус ответа и что
        # фотография с именем исходного файла существует в базе данных.
        file_content = storage.read_bytes(self.image_path)
        file_name = Path(self.image_path).name
        data = {
            "image": SimpleUploadedFile(file_name, file_content),
            "album": album.pk,
            "public": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Photo.objects.filter(name=photo_name).exists())

    def test_tag_add_via_admin(self) -> None:
        """Проверяет, что тэги можно успешно добавлять через административную панель."""
        test_tag_name = "test"

        # Ссылка на форму добавления тэга в административной панели.
        url = ADMIN_URL + "gallery/tag/add/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Заполнить форму, отправить форму, проверить статус ответа.
        response = self.client.post(url, data={"name": test_tag_name})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Проверить, что тэг с указанным именем существует в базе данных и что слаг автоматически создан.
        queryset = Tag.objects.filter(name=test_tag_name)
        self.assertTrue(queryset.exists())
        tag = queryset.first()
        self.assertIsNotNone(tag)
        if tag:
            self.assertEqual(tag.slug, "test")

    def test_album_add_via_admin(self) -> None:
        """Проверяет, что альбомы можно успешно добавлять через административную панель."""
        test_album_name = "Test album"

        # Ссылка на форму добавления альбома в административной панели.
        url = ADMIN_URL + "gallery/album/add/"

        # Заполнить форму, отправить форму, проверить статус ответа.
        data = {
            "name": test_album_name,
            "photos-TOTAL_FORMS": 0,
            "photos-INITIAL_FORMS": 0,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Проверить, что альбом с указанным именем существует в базе данных и что слаг автоматически создан.
        albums = Album.objects.all()
        album = albums.first()
        self.assertTrue(albums.exists())
        if album:
            self.assertEqual(album.name, test_album_name)
            self.assertEqual(album.slug, "test-album")

    def test_album_admin_change(self) -> None:
        """Проверка представления для изменения альбома."""
        with self.subTest("Получение страницы GET-методом"):
            album = AlbumFactory(name="Test album")
            url = ADMIN_URL + f"gallery/album/{album.pk}/change/"
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

        with self.subTest("Изменение альбома POST-методом"):
            new_slug = "new-slug"
            data = {
                "name": album.name,
                "slug": new_slug,
                "photos-TOTAL_FORMS": 0,
                "photos-INITIAL_FORMS": 0,
            }
            response = self.client.post(url, data)
            album.refresh_from_db()
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertEqual(album.slug, new_slug)

    def test_album_upload_url_resolve(self) -> None:
        """Маршрут страницы пакетной загрузки фотографий корректно разрешается и имеет имя."""
        url = reverse("admin:gallery_album_upload")
        self.assertEqual(url, ADMIN_URL + "gallery/album/upload/")
        resolver_match = resolve(url)
        self.assertEqual(resolver_match.view_name, "admin:gallery_album_upload")

    def test_album_changelist_has_upload_button(self) -> None:
        """Список альбомов содержит кнопку перехода на страницу загрузки."""
        response = self.client.get(ADMIN_URL + "gallery/album/")
        self.assertContains(response, reverse("admin:gallery_album_upload"))
        self.assertContains(response, "Загрузить фотографии")

    def test_album_upload_page_displayed(self) -> None:
        """Страница пакетной загрузки доступна персоналу и содержит форму."""
        response = self.client.get(ADMIN_URL + "gallery/album/upload/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'name="album"')
        self.assertContains(response, 'name="photos"')

    def test_album_upload_page_not_available_for_others(self) -> None:
        """Страница пакетной загрузки недоступна обычному пользователю и анониму."""
        with self.subTest("Для пользователя с обычными правами"):
            self.client.login(username="testuser", password="12345")
            response = self.client.get(ADMIN_URL + "gallery/album/upload/")
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertIn("/admin/login/", response.url)

        with self.subTest("Для анонимного пользователя"):
            self.client.logout()
            response = self.client.get(ADMIN_URL + "gallery/album/upload/")
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertIn("/admin/login/", response.url)

    def test_album_upload_creates_photos(self) -> None:
        """Пакетная загрузка создает фотографии в выбранном альбоме."""
        files = [self._uploaded_image("admin_upload_1.jpg"), self._uploaded_image("admin_upload_2.jpg")]
        data = {"album": self.album.pk, "photos": files}
        response = self.client.post(ADMIN_URL + "gallery/album/upload/", data, follow=True)

        self.assertRedirects(response, reverse("admin:gallery_album_change", args=[self.album.pk]))
        photos = Photo.objects.filter(album=self.album, name__startswith="admin_upload")
        self.assertEqual(photos.count(), 2)
        for photo in photos:
            self.assertTrue(photo.image.storage.exists(photo.image.name))
        self.assertContains(response, "Загружено 2 фотографий в альбом Тестовый альбом")

    def test_album_upload_invalid_file_shows_error(self) -> None:
        """Невалидный файл не создает фотографию, ошибка выводится сообщением."""
        file = SimpleUploadedFile(name="not_image.jpg", content=b"Not an image", content_type="image/jpeg")
        data = {"album": self.album.pk, "photos": [file]}
        response = self.client.post(ADMIN_URL + "gallery/album/upload/", data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(Photo.objects.filter(album=self.album, name="not_image").exists())
        # Кавычки в сообщении экранируются шаблонизатором.
        self.assertContains(response, "not_image.jpg")
        self.assertContains(response, "не является изображением")

    def test_album_upload_mixed_files(self) -> None:
        """В смешанной пачке валидные файлы создаются, невалидные дают ошибку."""
        files = [self._uploaded_image("admin_upload_1.jpg")]
        files.append(SimpleUploadedFile(name="not_image.jpg", content=b"Not an image", content_type="image/jpeg"))
        data = {"album": self.album.pk, "photos": files}
        response = self.client.post(ADMIN_URL + "gallery/album/upload/", data, follow=True)

        self.assertContains(response, "не является изображением")
        self.assertContains(response, "Загружено 1 фотографий в альбом Тестовый альбом")
        self.assertEqual(Photo.objects.filter(album=self.album, name="admin_upload_1").count(), 1)
        self.assertFalse(Photo.objects.filter(album=self.album, name="not_image").exists())
