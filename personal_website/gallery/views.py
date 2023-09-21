from django.db.models import QuerySet
from django.views.generic import DetailView, ListView, TemplateView

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
