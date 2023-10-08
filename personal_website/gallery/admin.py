from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from tinymce.widgets import TinyMCE

from gallery.forms import AlbumForm
from gallery.models import Album, Photo, Tag

formfield_overrides = {
    models.TextField: {"widget": TinyMCE()},
}


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели фотографии в панели администрирования Django.
    """

    model = Photo
    formfield_overrides = formfield_overrides
    fields = (
        "image",
        "name",
        "slug",
        "image_preview",
        "description",
        "album",
        "public",
        "tags",
        "uploaded_at",
        "modified_at",
    )
    readonly_fields = ("image_preview", "uploaded_at", "modified_at")
    list_display = ("name", "uploaded_at", "modified_at", "public", "image_thumbnail")
    list_filter = ("tags", "album")
    ordering = ("-modified_at",)

    @admin.display(description="Миниатюра")
    def image_thumbnail(self, obj: Photo):
        """
        Получить миниатюру фотографии для административной панели.
        """
        if obj.image:
            return mark_safe(f"<img src='{obj.image_thumbnail.url}'/>")
        return ""

    @admin.display(description="Превью")
    def image_preview(self, obj: Photo):
        """
        Получить превью фотографии для административной панели.
        """
        if obj.image:
            return mark_safe(f"<img src='{obj.image_preview.url}'/>")
        return ""


class PhotoInline(admin.TabularInline):
    model = Photo
    fields = (
        "image",
        "name",
        "image_thumbnail",
        "public",
    )
    readonly_fields = ("image_thumbnail",)
    extra = 5

    @admin.display(description="Миниатюра")
    def image_thumbnail(self, obj: Photo):
        """
        Получить миниатюру фотографии для административной панели.
        """
        if obj.image:
            return mark_safe(f"<img src='{obj.image_thumbnail.url}'/>")
        return ""


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели фотоальбома в панели администрирования Django.
    """

    inlines = [PhotoInline]
    form = AlbumForm
    fields = (
        "name",
        "description",
        "slug",
        "cover",
        "cover_preview",
        "tags",
        "created_at",
        "updated_at",
        "photos_count",
        "public_photos_count",
    )
    formfield_overrides = formfield_overrides
    readonly_fields = (
        "created_at",
        "updated_at",
        "cover_preview",
        "cover_preview",
        "photos_count",
        "public_photos_count",
    )
    list_display = (
        "name",
        "created_at",
        "updated_at",
        "public",
        "cover_thumbnail",
        "photos_count",
        "public_photos_count",
    )
    list_filter = ("tags",)

    @admin.display(description="Обложка")
    def cover_thumbnail(self, obj: Album):
        """
        Получить миниатюру обложки альбома для административной панели.
        """
        cover: Photo = obj.cover
        if cover:
            return mark_safe(f"<img src='{cover.image_thumbnail.url}'/>")
        return ""

    @admin.display(description="Обложка")
    def cover_preview(self, obj: Album):
        """
        Получить превью обложки альбома для административной панели.
        """
        cover: Photo = obj.cover
        if cover:
            return mark_safe(f"<img src='{cover.image_preview.url}'/>")
        return ""

    @admin.display(description="Фотографий")
    def photos_count(self, obj: Album):
        return obj.photos_count

    @admin.display(description="Публичных фотографий")
    def public_photos_count(self, obj: Album):
        return obj.public_photos_count


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели тэга в панели администрирования Django.
    """

    model = Tag
    formfield_overrides = formfield_overrides
    list_display = ("name",)
