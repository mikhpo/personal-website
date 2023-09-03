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
    readonly_fields = ("uploaded", "modified")
    list_display = ("name", "uploaded", "modified", "public", "thumbnail")
    list_filter = ("tags", "album")

    def thumbnail(self, obj: Photo):
        """
        Получить миниатюру фотографии для административной панели.
        """
        if obj.image:
            return mark_safe(f"<img src='{obj.image_thumbnail.url}'/>")
        return ""

    thumbnail.short_description = "Миниатюра"


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели фотоальбома в панели администрирования Django.
    """

    form = AlbumForm
    formfield_overrides = formfield_overrides
    readonly_fields = ("created", "updated")
    list_display = ("name", "created", "updated", "public", "thumbnail")
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
