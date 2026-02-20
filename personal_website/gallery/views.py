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
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormView
from PIL import Image, UnidentifiedImageError

from gallery.forms import UploadForm
from gallery.models import Album, Photo, Tag

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

logger = logging.getLogger(settings.PROJECT_NAME)


class GalleryHomeView(TemplateView):
    """Представление главной страницы галереи."""

    template_name = "gallery/gallery_home.html"

    def get_context_data(self, **kwargs) -> dict:
        """Добавить альбомы и тэги в контекст."""
        context = super().get_context_data(**kwargs)
        context["albums"] = Album.published.all()
        context["tags"] = Tag.objects.all()
        return context


class AlbumDetailView(DetailView):
    """Представление детальной страницы альбома."""

    model = Album
    template_name = "gallery/album_detail.html"
    context_object_name = "album"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self) -> "QuerySet[Album]":
        """Возвращать только публичные альбомы для обычных пользователей."""
        if hasattr(self.request.user, "is_staff") and self.request.user.is_staff:
            return Album.objects.all()
        return Album.published.all()


class PhotoDetailView(DetailView):
    """Представление детальной страницы фотографии."""

    model = Photo
    template_name = "gallery/photo_detail.html"
    context_object_name = "photo"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self) -> "QuerySet[Photo]":
        """Возвращать только публичные фотографии для обычных пользователей."""
        if hasattr(self.request.user, "is_staff") and self.request.user.is_staff:
            return Photo.objects.all()
        return Photo.published.all()


class TagDetailView(DetailView):
    """Представление детальной страницы тэга."""

    model = Tag
    template_name = "gallery/tag_detail.html"
    context_object_name = "tag"
    slug_field = "slug"
    slug_url_kwarg = "slug"


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
            messages.add_message(
                self.request,
                messages.SUCCESS,
                message=mark_safe(
                    f"Загружено <b>{counter}</b> фотографий в альбом "
                    f'<a href="{url}" class="alert-link">{album.name}</a>',
                ),
            )
            message = f"Загружено {counter} фотографий в альбом {album.name}"
            logger.info(message)

        return super().form_valid(form)
