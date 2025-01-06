"""Представления раздела галереи."""

import logging
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView
from PIL import Image, UnidentifiedImageError

from gallery.forms import UploadForm
from gallery.models import Album, Photo, Tag

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(settings.PROJECT_NAME)


class GalleryHomeView(TemplateView):
    """Предствление главной страницы галереи."""

    template_name = "gallery/gallery_home.html"

    def get_context_data(self, **kwargs) -> dict:
        """Добавить альбомы и тэги в контекст."""
        context = super().get_context_data(**kwargs)
        context["albums"] = Album.published.all()
        context["tags"] = Tag.objects.all()
        return context


class PhotoDetailView(DetailView):
    """Представление для показа единственной фотографии."""

    model = Photo
    template_name = "gallery/photo_detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавить в контекст следующую и предыдущую фотографии из альбома, а также все тэги фотографии."""
        context = super().get_context_data(**kwargs)
        obj: Photo = self.get_object()

        album_photos = Photo.published.filter(album=obj.album)
        next_photos = list(
            filter(
                lambda photo: photo.datetime_taken > obj.datetime_taken,
                sorted(album_photos, key=lambda photo: photo.datetime_taken),
            ),
        )
        previous_photos = list(
            filter(
                lambda photo: photo.datetime_taken < obj.datetime_taken,
                sorted(album_photos, key=lambda photo: photo.datetime_taken, reverse=True),
            ),
        )
        context["next_photo"] = next_photos[0] if next_photos else None
        context["previous_photo"] = previous_photos[0] if previous_photos else None
        context["tags"] = obj.tags.all()
        return context


class PhotoListView(ListView):
    """Отображение списка фотографий."""

    model = Photo
    template_name = "gallery/photo_list.html"
    paginate_by = 40

    def get_queryset(self) -> list[Photo]:  # type: ignore[override]
        """Отсортировать набор фотографий от новых к старым."""
        photos = Photo.published.all()
        return sorted(photos, key=lambda photo: photo.datetime_taken, reverse=True)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавить в контекст набор всхе тэгов фотографии."""
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        return context


class AlbumDetailView(DetailView):
    """Представление для показа альбома."""

    model = Album
    template_name = "gallery/album_detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавить в контекст все фотографии альбома, отсортированные по времени съемки, и все тэги."""
        context = super().get_context_data(**kwargs)
        album: Album = context["album"]

        # Получить коллекцию фотографий из даного альбома.
        photos: QuerySet[Photo] = album.photo_set.filter(public=True)

        # Добавить фотографии в контекст, отсортировав от старых к новым.
        context["photos"] = sorted(photos, key=lambda photo: photo.datetime_taken)
        context["tags"] = album.tags.all()
        return context


class AlbumListView(ListView):
    """Представление для показа списка альбомов."""

    model = Album
    template_name = "gallery/album_list.html"
    queryset = Album.published.all()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавить все тэги в контекст ответа."""
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        return context


class TagDetailView(DetailView):
    """Представление для просмотра фотографий и альбомов по тэгу."""

    model = Tag
    template_name = "gallery/tag_detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавить объекты в контекст представления.

        - Альбомы, отсортированные по дате создания, фотографии;
        - Фотогафии, отсортированные по времени съемки;
        - Все тэги.
        """
        # Получить тэг из контекста запроса
        context = super().get_context_data(**kwargs)
        tag: Tag = context["tag"]

        # Получить альбомы и фотографии по данному тэгу.
        albums: QuerySet[Album] = tag.tag_albums.all()
        photos: QuerySet[Photo] = tag.tag_photos.all()

        # Добавить полученные альбомы и фотографии в контекст.
        # Отсортирофать альбомы и фотографии от новых к старым.
        context["albums"] = sorted(albums, key=lambda album: album.created_at, reverse=True)
        context["photos"] = sorted(photos, key=lambda photo: photo.datetime_taken, reverse=True)
        context["tags"] = Tag.objects.all()
        return context


@method_decorator(staff_member_required, "dispatch")
class UploadFormView(FormView):
    """Представление для пакетной загрузки фотографий в альбом."""

    template_name = "gallery/upload.html"
    form_class = UploadForm
    success_url = reverse_lazy("gallery:gallery")

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавить тэги в контекст."""
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        return context

    def post(self, request: HttpRequest, *args: tuple, **kwargs: dict) -> HttpResponse:  # noqa: ARG002
        """Проверить форму на валидность после отправки."""
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form: UploadForm) -> HttpResponse:
        """Верифицировать и создать каждую загруженную фотографию."""
        # Получение данных из отправленной формы.
        data: dict = form.cleaned_data
        photos = data["photos"]
        album: Album = data["album"]

        # Цикл для каждой фотографии из отправленной формы.
        counter = 0  # инициализация счетчика загруженных фотографий
        for photo in photos:
            try:
                image = Image.open(photo)
                image.verify()
                Photo.objects.create(image=photo, album=album)
                message = f"Загружена фотография {photo} в альбом {album}"
                logger.debug(message)
                counter += 1
            except UnidentifiedImageError:  # noqa: PERF203
                message = f'Загруженный файл "{photo}" не является изображением'
                messages.add_message(self.request, messages.ERROR, message)
                logger.exception(message)
            except Exception as error:
                message = f'Ошибка загрузки фотографии в альбом "{album}": "{error}"'
                messages.add_message(self.request, messages.ERROR, message)
                logger.exception(message)

        #  Если хотя бы одна фотография заружена в альбом.
        if counter:
            url = album.get_absolute_url()
            string = (
                f"Загружено <b>{counter}</b> фотографий в альбом "
                f'<a href="{url}" class="alert-link">{album.name}</a>'
            )
            safe_string = mark_safe(string)
            messages.add_message(self.request, messages.SUCCESS, safe_string)
            message = f"Загружено {counter} фотографий в альбом {album.name}"
            logger.info(message)

        return super().form_valid(form)
