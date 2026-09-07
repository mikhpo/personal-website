"""Конфигурация приложения блога."""

from django.apps import AppConfig


class BlogConfig(AppConfig):  # noqa: D101
    name = "blog"
    verbose_name = "Блог"
    default_auto_field = "django.db.models.AutoField"

    def ready(self) -> None:
        """При инициации приложения включить аудит изменений моделей."""
        # Импорт внутри ready обязателен: реестр моделей доступен
        # только после загрузки приложений
        from auditlog.registry import auditlog  # noqa: PLC0415

        from blog.models import Article, Category, Comment, Series, Topic  # noqa: PLC0415

        auditlog.register(Article, m2m_fields={"categories", "topics", "series"})
        auditlog.register(Category)
        auditlog.register(Series)
        auditlog.register(Topic)
        auditlog.register(Comment)
