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
        "preview",
        "description",
        "album",
        "public",
        "tags",
        "uploaded_at",
        "modified_at",
    )
    readonly_fields = ("preview", "uploaded_at", "modified_at")
    list_display = ("name", "uploaded_at", "modified_at", "public", "thumbnail")
    list_filter = ("tags", "album")
    ordering = ("-modified_at",)

    def thumbnail(self, obj: Photo):
        """
        Получить миниатюру фотографии для административной панели.
        """
        if obj.image:
            return mark_safe(f"<img src='{obj.image_thumbnail.url}'/>")
        return ""

    def preview(self, obj: Photo):
        """
        Получить превью фотографии для административной панели.
        """
        if obj.image:
            return mark_safe(f"<img src='{obj.image_preview.url}'/>")
        return ""

    thumbnail.short_description = "Миниатюра"
    preview.short_description = "Превью"


class PhotoInline(admin.TabularInline):
    model = Photo
    exclude = ("description", "slug")
    extra = 5


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели фотоальбома в панели администрирования Django.
    """

    inlines = [PhotoInline]
    form = AlbumForm
    formfield_overrides = formfield_overrides
    readonly_fields = ("created_at", "updated_at")
    list_display = ("name", "created_at", "updated_at", "public", "thumbnail")
    list_filter = ("tags",)

    def thumbnail(self, obj: Album):
        """
        Получить миниатюру обложки альбома для административной панели.
        """
        if obj.cover:
            return mark_safe(f"<img src='{obj.cover.image_thumbnail.url}'/>")
        return ""

    thumbnail.short_description = "Обложка"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели тэга в панели администрирования Django.
    """

    model = Tag
    formfield_overrides = formfield_overrides
    list_display = ("name",)
