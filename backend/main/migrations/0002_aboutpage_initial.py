"""Создание единственной записи страницы Обо мне."""

from django.db import migrations


def create_about_page(apps, schema_editor) -> None:
    """Создает пустую запись страницы, если она отсутствует."""
    AboutPage = apps.get_model("main", "AboutPage")
    AboutPage.objects.get_or_create(pk=1)


def delete_about_page(apps, schema_editor) -> None:
    """Удаляет запись страницы при откате миграции."""
    AboutPage = apps.get_model("main", "AboutPage")
    AboutPage.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_about_page, delete_about_page),
    ]
