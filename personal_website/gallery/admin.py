from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from gallery.forms import AlbumForm
from gallery.models import Album, Photo, Tag
from tinymce.widgets import TinyMCE

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

    def image_thumbnail(self, obj: Photo):
        """
        Получить миниатюру фотографии для административной панели.
        """
        if obj.image:
            return mark_safe(f"<img src='{obj.image_thumbnail.url}'/>")
        return ""

    def image_preview(self, obj: Photo):
        """
        Получить превью фотографии для административной панели.
        """
        if obj.image:
            return mark_safe(f"<img src='{obj.image_preview.url}'/>")
        return ""

    image_thumbnail.short_description = "Миниатюра"
    image_preview.short_description = "Превью"


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

    def image_thumbnail(self, obj: Photo):
        """
        Получить миниатюру фотографии для административной панели.
        """
        if obj.image:
            return mark_safe(f"<img src='{obj.image_thumbnail.url}'/>")
        return ""

    image_thumbnail.short_description = "Миниатюра"


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
    )
    formfield_overrides = formfield_overrides
    readonly_fields = (
        "created_at",
        "updated_at",
        "cover_preview",
        "cover_preview",
    )
    list_display = ("name", "created_at", "updated_at", "public", "cover_thumbnail")
    list_filter = ("tags",)

    def cover_thumbnail(self, obj: Album):
        """
        Получить миниатюру обложки альбома для административной панели.
        """
        cover: Photo = obj.cover
        if cover:
            return mark_safe(f"<img src='{cover.image_thumbnail.url}'/>")
        return ""

    def cover_preview(self, obj: Album):
        """
        Получить превью обложки альбома для административной панели.
        """
        cover: Photo = obj.cover
        if cover:
            return mark_safe(f"<img src='{cover.image_preview.url}'/>")
        return ""

    cover_thumbnail.short_description = "Обложка"
    cover_preview.short_description = "Обложка"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели тэга в панели администрирования Django.
    """

    model = Tag
    formfield_overrides = formfield_overrides
    list_display = ("name",)
