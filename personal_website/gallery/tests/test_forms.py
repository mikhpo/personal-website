import os

from django.conf import settings
from django.test import TestCase, override_settings

from gallery.forms import AlbumForm
from gallery.models import Album, Photo
from utils import list_file_paths


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, "media"))
class GalleryFormsTest(TestCase):
    """
    Тестирование форм приложения галереи.
    """

    def test_no_cover_photos_for_new_album(self):
        """
        Проверяет, что при создании нового альбома для выбора фотографии на обложку не доступно ни одной фотографии.
        """
        form = AlbumForm()
        self.assertEqual(form.instance.pk, None)
        self.assertQuerySetEqual(form.fields["cover"].queryset, Photo.objects.none())

    def test_album_default_is_public(self):
        """
        Проверяет, что по умолчанию альбом создается публичным.
        """
        form = AlbumForm()
        public = form.fields["public"].initial
        self.assertEqual(public, True)

    def test_cover_photos_from_album(self):
        """
        Проверяет, что для выбора обложки альбома доступны фотографии только из этого альбома.
        """
        # Создать альбом для размещения тосканских фотографий.
        tuscany_album = Album.objects.create(name="Тоскана")
        langtang_album = Album.objects.create(name="Лангтанг")

        # Создать фотографии в базе данных, загрузив их с диска.
        images = list_file_paths(settings.TEST_IMAGES_DIR)
        for image in images:
            if "Tuscany" in image:
                Photo.objects.create(image=image, public=True, album=tuscany_album)
            else:
                Photo.objects.create(image=image, public=False, album=langtang_album)
        tuscany_photos = Photo.objects.filter(name__contains="Tuscany")
        langtang_photos = Photo.objects.filter(name__contains="Langtang")

        # Инициировать форму редактирования тосканского альбома.
        form = AlbumForm(instance=tuscany_album)

        # Получить список фотографий, доступных для выбора в качестве обложки.
        cover_choices = form.fields["cover"].queryset

        # Убедиться, что каждая из тосканских фотографий содержится в списке.
        for tuscany_photo in tuscany_photos:
            self.assertIn(tuscany_photo, cover_choices)

        # Убедиться, что ни одна из лангтангских фотографий не содержится в списке.
        for langtang_photo in langtang_photos:
            self.assertNotIn(langtang_photo, cover_choices)

        # Убедиться, что список фотографий для выбора соответствует полному списку фотографий из Тосканы.
        self.assertQuerySetEqual(cover_choices, tuscany_photos)
