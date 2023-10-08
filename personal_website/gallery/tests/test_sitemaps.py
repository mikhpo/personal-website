from http import HTTPStatus

from django.test import TestCase
from django.utils import timezone

from gallery.models import Album, Photo, Tag
from personal_website.utils import list_image_paths

SITEMAP_URL = "/sitemap.xml"


class GallerySitemapTest(TestCase):
    """
    Тестирование карты галереи.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Метод применяется один раз перед выполнением тестов класса.
        """
        # Создать теги.
        for tag in ["Путешествия", "Италия", "Тоскана", "Непал", "Лангтанг"]:
            Tag.objects.create(name=tag)

        # Создать альбомы.
        cls.public_album = Album.objects.create(
            name="Тоскана",
            description="Фотографии из путешествия по Тоскане осенью 2013 года",
            public=True,
        )
        cls.private_album = Album.objects.create(
            name="Лангтанг",
            description="Фотографии из путешествия по Лангтангу весной 2014 года",
            public=False,
        )

        # Создать фотографии в базе данных из картинок в директории проекта.
        images = list_image_paths()
        for image in images:
            if "Tuscany" in image:
                Photo.objects.create(image=image, public=True, album=cls.public_album)
            else:
                Photo.objects.create(image=image, public=False, album=cls.private_album)

    def test_tag_sitemap(self):
        """
        Проверить, что все тэги добавляются в карту сайта.
        """
        tags = Tag.objects.all()
        response = self.client.get(SITEMAP_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        for tag in tags:
            self.assertTrue(tag.get_absolute_url() in content)

    def test_album_sitemap(self):
        """
        Проверить, что альбомы присутствуют в карте сайта, но только публичные.
        """
        response = self.client.get(SITEMAP_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        local_time = timezone.localtime(self.public_album.updated_at)
        modified_at_date = str(local_time.date())
        self.assertTrue(self.public_album.get_absolute_url() in content)
        self.assertFalse(self.private_album.get_absolute_url() in content)
        self.assertTrue(modified_at_date in content)

    def test_photo_sitemap(self):
        """
        Проверить, что фотографии присутствуют в карте сайта, но только публичные.
        """
        public_photos = Photo.objects.filter(public=True)
        private_photos = Photo.objects.filter(public=False)
        response = self.client.get(SITEMAP_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = str(response.content)
        for photo in public_photos:
            self.assertTrue(photo.get_absolute_url() in content)
        for photo in private_photos:
            self.assertFalse(photo.get_absolute_url() in content)
