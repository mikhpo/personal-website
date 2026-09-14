"""Представления раздела галереи."""

import logging
from typing import TYPE_CHECKING, Any, ClassVar

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView

from gallery.forms import UploadForm
from gallery.models import Album, Photo, Tag
from gallery.services import ensure_embed_preview, upload_error_message, upload_photos_to_album

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

logger = logging.getLogger(settings.PROJECT_NAME)


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
        """Добавить ID предыдущей и следующей фотографий и размеры превью для вставок."""
        context: dict[str, Any] = super().get_context_data(**kwargs)
        photo: Photo = self.object
        album: Album = photo.album
        context["embed_sizes"] = list(settings.GALLERY_EMBED_SIZES)

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


class EmbedPhotoView(View):
    """Постоянная ссылка на превью фотографии для вставки в статьи и сторонние ресурсы.

    Ссылка публична и не зависит от публикации фотографии: ранее созданные
    вставки продолжают работать после скрытия фотографии из галереи и
    прекращают работу только после ее удаления (404). Превью отдается в
    формате исходного изображения. Расширение в ссылке информационное:
    при смене формата исходника ссылка продолжает работать - редирект
    ведет к актуальному файлу превью. Ответ - редирект на файл в хранилище,
    при первом обращении файл генерируется.
    """

    http_method_names: ClassVar[list[str]] = ["get"]

    def get(self, request: HttpRequest, pk: str, size: str, ext: str) -> HttpResponse:  # noqa: ARG002
        """Перенаправить на файл превью выбранного размера, при необходимости сгенерировать его."""
        photo_pk = int(pk)
        preview_size = int(size)
        if preview_size not in settings.GALLERY_EMBED_SIZES:
            msg = "Размер превью не поддерживается"
            raise Http404(msg)
        photo = get_object_or_404(Photo.objects.all(), pk=photo_pk)
        try:
            embed_name = ensure_embed_preview(photo, preview_size)
        except (FileNotFoundError, OSError):
            logger.exception("Не удалось подготовить превью для вставки фотографии %s", photo_pk)
            msg = "Файл изображения недоступен"
            raise Http404(msg) from None
        return redirect(photo.image.storage.url(embed_name))


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
