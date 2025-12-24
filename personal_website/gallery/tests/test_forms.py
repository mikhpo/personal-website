"""Тесты форм галереи."""

from django.test import TestCase

from gallery.factories import AlbumFactory, PhotoFactory
from gallery.forms import AlbumForm
from gallery.models import Photo
from personal_website.utils import list_file_paths


class GalleryFormsTest(TestCase):
    """Тестирование форм приложения галереи."""

    def test_no_cover_photos_for_new_album(self) -> None:
        """
        Проверяет, что при создании нового альбома для выбора
        фотографии на обложку не доступно ни одной фотографии.
        """
        form = AlbumForm()
        self.assertEqual(form.instance.pk, None)
        form_cover_qs = form.fields["cover"].queryset
        none_photo_qs = Photo.objects.none()
        self.assertQuerySetEqual(form_cover_qs, none_photo_qs)  # type: ignore[arg-type]

    def test_album_default_is_public(self) -> None:
        """Проверяет, что по умолчанию альбом создается публичным."""
        form = AlbumForm()
        public = form.fields["public"].initial
        self.assertEqual(public, True)

    def test_cover_photos_from_album(self) -> None:
        """Проверяет, что для выбора обложки альбома доступны фотографии только из этого альбома."""
        # Создать альбом для размещения тосканских фотографий.
        tuscany_album = AlbumFactory(name="Тоскана")
        langtang_album = AlbumFactory(name="Лангтанг")

        # Создать фотографии в базе данных, загрузив их с диска.
        test_images_dir = "gallery/photos"
        images = list_file_paths(test_images_dir)
        for image in images:
            # Если в названии файла фотографии есть Tuscany, то создать фотографию в тосканском альбоме.
            if "Tuscany" in image:
                PhotoFactory(image=image, name=None, public=True, album=tuscany_album)
            # В ином случае создать фотографию в лангатангском альбоме.
            else:
                PhotoFactory(image=image, name=None, public=False, album=langtang_album)
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
        self.assertQuerySetEqual(cover_choices, tuscany_photos, ordered=False)  # type: ignore[arg-type]
