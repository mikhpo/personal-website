"""Представления раздела галереи."""

from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView

from gallery.forms import UploadForm
from gallery.models import Album, Photo, Tag
from gallery.services import upload_error_message, upload_photos_to_album

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class GalleryHomeView(TemplateView):
    """Представление главной страницы галереи."""

    template_name = "gallery/gallery_home.html"

    def get_context_data(self, **kwargs) -> dict:
        """Добавить поисковый запрос, альбомы и тэги в контекст.

        Поисковый запрос попадает в пропы SearchForm и AlbumList; набор
        альбомов фильтруется на клиенте через API (?search=), тэги
        не фильтруются.
        """
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["albums"] = Album.published.all()
        context["tags"] = Tag.objects.all()
        return context


class AlbumListView(ListView):
    """Представление для показа списка альбомов."""

    model = Album
    template_name = "gallery/album_list.html"
    queryset = Album.published.all()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавить все тэги и поисковый запрос в контекст ответа."""
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        context["search"] = self.request.GET.get("search", "")
        return context


class AlbumDetailView(DetailView):
    """Представление детальной страницы альбома."""

    model = Album
    template_name = "gallery/album_detail.html"
    context_object_name = "album"
    pk_url_kwarg = "pk"

    def get_queryset(self) -> "QuerySet[Album]":
        """Возвращает все альбомы.

        Фильтрация по public выполняется в списках (см. AlbumViewSet);
        детальный просмотр доступен всем.
        """
        return Album.objects.all()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавить URL API альбома в контекст."""
        context = super().get_context_data(**kwargs)
        context["album_api_url"] = f"/api/gallery/albums/{self.object.pk}/"
        return context


class PhotoListView(ListView):
    """Отображение списка фотографий."""

    model = Photo
    template_name = "gallery/photo_list.html"
    paginate_by = 40

    def get_queryset(self) -> "QuerySet[Photo]":  # type: ignore[override]
        """Отсортировать набор фотографий по дате съемки."""
        return Photo.published.all().order_by("-taken_at")

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавить в контекст набор всех тэгов и поисковый запрос фотографии."""
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        context["search"] = self.request.GET.get("search", "")
        return context


class PhotoDetailView(DetailView):
    """Представление детальной страницы фотографии."""

    model = Photo
    template_name = "gallery/photo_detail.html"
    context_object_name = "photo"
    pk_url_kwarg = "pk"

    def get_queryset(self) -> "QuerySet[Photo]":
        """Возвращает все фотографии.

        Фильтрация по public выполняется в списках (см. PhotoViewSet);
        детальный просмотр доступен всем.
        """
        return Photo.objects.all()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавить ID предыдущей и следующей фотографий в контекст."""
        context: dict[str, Any] = super().get_context_data(**kwargs)
        photo: Photo = self.object
        album: Album = photo.album

        # Навигация prev/next только по публичным фотографиям альбома:
        # скрытые не предлагаются соседями ни при прямом заходе, ни из списков.
        all_photos_qs: QuerySet[Photo] = album.photos.filter(public=True).order_by("taken_at")

        previous_photo = all_photos_qs.filter(taken_at__lt=photo.taken_at).order_by("-taken_at").first()
        if previous_photo:
            context["previous_photo_id"] = previous_photo.pk

        next_photo = all_photos_qs.filter(taken_at__gt=photo.taken_at).order_by("taken_at").first()
        if next_photo:
            context["next_photo_id"] = next_photo.pk

        return context


class TagDetailView(DetailView):
    """Представление детальной страницы тэга."""

    model = Tag
    template_name = "gallery/tag_detail.html"
    context_object_name = "tag"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавить все тэги в контекст ответа."""
        context = super().get_context_data(**kwargs)
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
        album: Album = data["album"]
        results = upload_photos_to_album(album, data["photos"])

        # Отдельное сообщение об ошибке для каждого необработанного файла.
        for result in results:
            if result.error is not None:
                messages.add_message(self.request, messages.ERROR, upload_error_message(result, album))

        #  Если хотя бы одна фотография заружена в альбом.
        uploaded = [result for result in results if result.success]
        if uploaded:
            url = album.get_absolute_url()
            messages.add_message(
                self.request,
                messages.SUCCESS,
                message=mark_safe(
                    f"Загружено <b>{len(uploaded)}</b> фотографий в альбом "
                    f'<a href="{url}" class="alert-link">{album.name}</a>',
                ),
            )

        return super().form_valid(form)
