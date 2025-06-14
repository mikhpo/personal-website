"""Представления объектов галереи в административной панели Django."""

from adminsortable2.admin import SortableAdminMixin  # type: ignore[import-untyped]
from django.contrib import admin
from django.db import models
from django.utils.safestring import SafeText, mark_safe
from tinymce.widgets import TinyMCE  # type: ignore[import-untyped]

from gallery.forms import AlbumForm
from gallery.models import Album, Photo, Tag
from personal_website.utils import format_local_datetime

FORMFIELD_OVERRIDES = {models.TextField: {"widget": TinyMCE()}}


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """Настройки отображения модели фотографии в панели администрирования Django."""

    model = Photo
    formfield_overrides = FORMFIELD_OVERRIDES  # type: ignore[assignment]
    fields = (
        "image",
        "name",
        "slug",
        "image_preview",
        "description",
        "album",
        "public",
        "tags",
        "taken_at",
        "uploaded_at",
        "modified_at",
        "exif_table",
    )
    readonly_fields = (
        "image_preview",
        "uploaded_at",
        "modified_at",
        "taken_at",
        "exif_table",
    )
    list_display = (
        "name",
        "uploaded_at",
        "modified_at",
        "public",
        "image_thumbnail",
    )
    list_filter = ("tags", "album")
    ordering = ("-modified_at",)

    @admin.display(description="Миниатюра")
    def image_thumbnail(self, obj: Photo) -> SafeText | str:
        """Получить миниатюру фотографии для административной панели."""
        if obj.image:
            return mark_safe(f"<img src='{obj.image_thumbnail.url}'/>")
        return ""

    @admin.display(description="Превью")
    def image_preview(self, obj: Photo) -> SafeText | str:
        """Получить превью фотографии для административной панели."""
        if obj.image:
            return mark_safe(f"<img src='{obj.image_preview.url}'/>")
        return ""

    @admin.display(description="Создана")
    def taken_at(self, obj: Photo) -> str:
        """Дата и время съемки."""
        return format_local_datetime(obj.datetime_taken)

    @admin.display(description="EXIF")
    def exif_table(self, obj: Photo) -> SafeText | str:
        """Таблица с данными EXIF."""
        table_html = f"""
            <table>
                <tr>
                    <td>Камера</td>
                    <td>{obj.camera}</td>
                </tr>
                <tr>
                    <td>Объектив</td>
                    <td>{obj.lens_model}</td>
                </tr>
                <tr>
                    <td>Фокусное расстояние</td>
                    <td>{obj.focal_length} мм</td>
                </tr>
                <tr>
                    <td>Диафрагма</td>
                    <td>{obj.aperture}</td>
                </tr>
                <tr>
                    <td>Выдержка</td>
                    <td>{obj.exposure} с</td>
                </tr>
                <tr>
                    <td>Светочувствительность</td>
                    <td>ISO {obj.iso }</td>
                </tr>
        </table>
    """
        return mark_safe(table_html)


class PhotoInline(admin.TabularInline):
    """Набор форм фотографий для показа в представлении альбома."""

    model = Photo
    fields = (
        "image",
        "name",
        "image_thumbnail",
        "public",
    )
    readonly_fields = ("image_thumbnail",)
    show_change_link = True
    extra = 5

    @admin.display(description="Миниатюра")
    def image_thumbnail(self, obj: Photo) -> SafeText | str:
        """Получить миниатюру фотографии для административной панели."""
        if obj.image:
            return mark_safe(f"<img src='{obj.image_thumbnail.url}'/>")
        return ""


@admin.register(Album)
class AlbumAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Настройки отображения модели фотоальбома в панели администрирования Django."""

    inlines = (PhotoInline,)
    form = AlbumForm
    formfield_overrides = FORMFIELD_OVERRIDES  # type: ignore[assignment]
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
        "order",
    )
    list_filter = ("tags",)

    @admin.display(description="Обложка")
    def cover_thumbnail(self, obj: Album) -> SafeText | str:
        """Получить миниатюру обложки альбома для административной панели."""
        cover: Photo = obj.cover
        if cover:
            return mark_safe(f"<img src='{cover.image_thumbnail.url}'/>")
        return ""

    @admin.display(description="Обложка")
    def cover_preview(self, obj: Album) -> SafeText | str:
        """Получить превью обложки альбома для административной панели."""
        cover: Photo = obj.cover
        if cover:
            return mark_safe(f"<img src='{cover.image_preview.url}'/>")
        return ""

    @admin.display(description="Фотографий")
    def photos_count(self, obj: Album) -> int:
        """Количество всех фотографий."""
        return obj.photos_count

    @admin.display(description="Публичных фотографий")
    def public_photos_count(self, obj: Album) -> int:
        """Количество публичных фотографий."""
        return obj.public_photos_count


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки отображения модели тэга в панели администрирования Django."""

    model = Tag
    formfield_overrides = FORMFIELD_OVERRIDES  # type: ignore[assignment]
    list_display = ("name",)
