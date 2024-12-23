"""Представления блога в административном сайте Django."""

from typing import Any

from django.contrib import admin
from django.db import models
from django.http import HttpRequest
from tinymce.widgets import TinyMCE

from blog.models import Article, Category, Comment, Series, Topic

FORMFIELD_OVERRIDES = {
    models.TextField: {"widget": TinyMCE()},
}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Настройки отображения модели статьи в панели администрирования Django."""

    model = Article

    # Стандартная форма тектового поля заменена на HTML форму TinyMCE.
    formfield_overrides = FORMFIELD_OVERRIDES

    list_display = ("title", "published_at", "modified_at", "public")
    list_filter = ("series", "topics", "categories", "public")

    fieldsets = (
        ("Содержание", {"fields": ["title", "description", "content"]}),
        ("Метаданные", {"fields": ["series", "topics", "categories"]}),
        ("Картинка", {"fields": ["image"]}),
        ("Служебные", {"fields": ["slug", "public", "published_at"]}),
    )

    readonly_fields = ("published_at",)

    # Автор фиксируется, но не редактируется.
    exclude = ("author",)

    def get_readonly_fields(self, request: HttpRequest, obj: Article | None = None) -> tuple | list:  # noqa: ARG002
        """Дату публикации можно изменить только при создании статьи, но не при редактировании."""
        if obj:
            return self.readonly_fields
        return []

    def save_model(self, request: HttpRequest, obj: Article, form: Any, change: Any) -> None:  # noqa: ANN401
        """
        При создании статьи через административный интерфейс текущий
        пользователь автоматически фиксируется как автор статьи.
        """
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройки отображения модели категории в панели администрирования Django."""

    model = Category
    list_display = ("name", "public", "slug", "image")
    list_filter = ("public",)


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    """Настройки отображения модели серии в панели администрирования Django."""

    model = Series
    list_display = ("name", "public", "slug", "image")
    list_filter = ("public",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Настройки отображения модели тем в панели администрирования Django."""

    model = Topic
    list_display = ("name", "public", "slug", "image")
    list_filter = ("public",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Настройки отображения модели комментариев в панели администрирования Django."""

    model = Comment
    formfield_overrides = FORMFIELD_OVERRIDES
    list_display = ("article", "author", "posted")
    list_filter = ("article", "author")
