"""Модели приложения Обо мне."""

from django.db import models


class About(models.Model):
    """Модель данных обо мне с редактируемым содержимым.

    Единственная запись таблицы хранит произвольный HTML-контент:
    контакты, ссылки на профили в социальных сетях, описание автора.
    Запись выводится на странице Обо мне и в API, контент редактируется
    в административном сайте через TinyMCE, поэтому состав и количество
    сведений ничем не ограничены.
    """

    content = models.TextField("Содержимое", blank=True)

    class Meta:  # noqa: D106
        verbose_name = "Обо мне"
        verbose_name_plural = "Обо мне"

    def __str__(self) -> str:
        """Строковое представление указывает назначение данных."""
        return "Обо мне"

    def save(self, *args, **kwargs) -> None:
        """Синглтон всегда сохраняется под фиксированным ключом."""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> tuple:  # noqa: ARG002
        """Удаление единственной записи запрещено - данные существуют всегда."""
        return (0, {})

    @classmethod
    def get_solo(cls) -> "About":
        """Возвращает единственную запись, создавая пустую при отсутствии."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
