from typing import Any

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView

from gallery.forms import UploadForm
from gallery.mixins import GalleryContentMixin
from gallery.models import Album, Photo, Tag


class GalleryHomeView(GalleryContentMixin, TemplateView):
    """
    Предствление главной страницы галереи.
    """

    template_name = "gallery/gallery_home.html"


class PhotoDetailView(DetailView):
    """
    Представление для показа единственной фотографии.
    """

    model = Photo
    template_name = "gallery/photo_detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        photo: Photo = self.get_object()
        context["next_photo"] = (
            Photo.published.filter(album=photo.album, pk__gt=photo.pk)
            .order_by("pk")
            .first()
        )
        context["previous_photo"] = (
            Photo.published.filter(album=photo.album, pk__lt=photo.pk)
            .order_by("pk")
            .last()
        )
        return context


class PhotoListView(ListView):
    """
    Отображение списка фотографий.
    """

    model = Photo
    template_name = "gallery/photo_list.html"

    def get_queryset(self):
        # Отсортировать набор фотографий от новых к старым.
        photos = Photo.published.all()
        photos_sorted = sorted(photos, key=lambda photo: photo.datetime_taken)
        return photos_sorted


class AlbumDetailView(DetailView):
    """
    Представление для показа альбома.
    """

    model = Album
    template_name = "gallery/album_detail.html"

    def get_queryset(self):
        album = super(AlbumDetailView, self).get_queryset()
        return album

    def get_context_data(self, **kwargs):
        context = super(AlbumDetailView, self).get_context_data(**kwargs)

        # Получить коллекцию фотографий из даного альбома.
        photos: QuerySet[Photo] = context["album"].photo_set.filter(public=True)

        # Добавить фотографии в контекст, отсортировав от старых к новым.
        context["photos"] = sorted(photos, key=lambda photo: photo.datetime_taken)
        return context


class AlbumListView(ListView):
    """
    Представление для показа списка альбомов.
    """

    model = Album
    template_name = "gallery/album_list.html"
    queryset = Album.published.all()


class TagDetailView(DetailView):
    """
    Представление для просмотра фотографий и альбомов по тэгу.
    """

    model = Tag
    template_name = "gallery/tag_detail.html"

    def get_context_data(self, **kwargs):
        # Получить тэг из контекста запроса
        context = super(TagDetailView, self).get_context_data(**kwargs)
        tag: Tag = context["tag"]

        # Получить альбомы и фотографии по данному тэгу.
        albums: QuerySet[Album] = tag.tag_albums.all()
        photos: QuerySet[Photo] = tag.tag_photos.all()

        # Добавить полученные альбомы и фотографии в контекст.
        # Отсортирофать альбомы и фотографии от новых к старым.
        context["albums"] = sorted(
            albums, key=lambda album: album.created_at, reverse=True
        )
        context["photos"] = sorted(
            photos, key=lambda photo: photo.datetime_taken, reverse=True
        )
        return context


class TagListView(ListView):
    """
    Представление для просмотра списка тегов.
    """

    model = Tag
    template_name = "gallery/tag_list.html"


@method_decorator(staff_member_required, "dispatch")
class UploadFormView(FormView):
    """
    Представление для пакетной загрузки фотографий в альбом.
    """

    template_name = "gallery/upload.html"
    form_class = UploadForm
    success_url = reverse_lazy("gallery:gallery")

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form: UploadForm):
        data: dict = form.cleaned_data
        photos = data["photos"]
        album = data["album"]
        for photo in photos:
            Photo.objects.create(image=photo, album=album)
        return super().form_valid(form)
