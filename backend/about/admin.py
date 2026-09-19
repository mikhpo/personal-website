"""Представление страницы Обо мне в административном сайте Django."""

from typing import ClassVar

from django.contrib import admin
from django.db import models
from django.http import HttpRequest
from tinymce.widgets import TinyMCE  # type: ignore[import-untyped]

from about.models import About


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    """Настройки отображения страницы Обо мне в панели администрирования Django.

    Запись в списке одна, поэтому добавление и удаление запрещены -
    доступна только правка содержимого страницы.
    """

    model = About

    # Стандартная форма текстового поля заменена на HTML форму TinyMCE.
    formfield_overrides: ClassVar[dict] = {models.TextField: {"widget": TinyMCE()}}  # type: ignore[assignment]

    def has_add_permission(self, request: HttpRequest) -> bool:  # noqa: ARG002
        """Добавление записи запрещено - страница Обо мне всегда одна."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj: About | None = None) -> bool:  # noqa: ARG002
        """Удаление записи запрещено - страница Обо мне существует всегда."""
        return False
