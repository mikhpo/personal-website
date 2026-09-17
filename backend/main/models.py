"""Модели главного раздела сайта."""

from django.db import models


class AboutPage(models.Model):
    """Модель страницы "Обо мне" с редактируемым содержимым.

    Единственная запись таблицы хранит произвольный HTML-контент страницы:
    контакты, ссылки на профили в социальных сетях, описание автора.
    Контент редактируется в административном сайте через TinyMCE,
    поэтому состав и количество сведений ничем не ограничены.
    """

    content = models.TextField("Содержимое страницы", blank=True)

    class Meta:  # noqa: D106
        verbose_name = "Страница Обо мне"
        verbose_name_plural = "Страница Обо мне"

    def __str__(self) -> str:
        """Строковое представление страницы указывает ее назначение."""
        return "Страница Обо мне"

    def save(self, *args, **kwargs) -> None:
        """Синглтон всегда сохраняется под фиксированным ключом."""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> tuple:  # noqa: ARG002
        """Удаление единственной записи запрещено - страница существует всегда."""
        return (0, {})

    @classmethod
    def get_solo(cls) -> "AboutPage":
        """Возвращает единственную запись страницы, создавая пустую при отсутствии."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
