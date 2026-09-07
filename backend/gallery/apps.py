"""Конфигурация приложения галереи."""

from django.apps import AppConfig


class GalleryConfig(AppConfig):  # noqa: D101
    name = "gallery"
    verbose_name = "Галерея"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """При инициации приложения включить аудит изменений моделей."""
        # Импорт внутри ready обязателен: реестр моделей доступен
        # только после загрузки приложений
        from auditlog.registry import auditlog  # noqa: PLC0415

        from gallery.models import Album, Photo, Tag  # noqa: PLC0415

        auditlog.register(Album, m2m_fields={"tags"})
        auditlog.register(Photo, m2m_fields={"tags"})
        auditlog.register(Tag)
