# Generated by Django 4.1.7 on 2023-05-01 13:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Album",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Наименование альбома",
                        max_length=255,
                        verbose_name="Наименование",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Описание альбома",
                        verbose_name="Описание",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Слаг альбома",
                        unique=True,
                        verbose_name="Слаг",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Дата и время создания альбома",
                        verbose_name="Создан",
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Дата и время последнего обновления альбома",
                        verbose_name="Обновлен",
                    ),
                ),
                (
                    "public",
                    models.BooleanField(
                        default=True,
                        help_text="Альбом публичный",
                        verbose_name="Публичный",
                    ),
                ),
            ],
            options={
                "verbose_name": "Альбом",
                "verbose_name_plural": "Альбомы",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Наименование тэга",
                        max_length=255,
                        verbose_name="Наименование",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Слаг тэга",
                        unique=True,
                        verbose_name="Слаг",
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, help_text="Описание тэга", verbose_name="Описание"),
                ),
            ],
            options={
                "verbose_name": "Тэг",
                "verbose_name_plural": "Тэги",
                "ordering": ["slug"],
            },
        ),
        migrations.CreateModel(
            name="Photo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(upload_to="gallery/photos/", verbose_name="Изображение"),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        help_text="Наименование фотографии",
                        max_length=255,
                        verbose_name="Наименование",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Описание фотографии",
                        verbose_name="Описание",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Слаг фотографии",
                        unique=True,
                        verbose_name="Слаг",
                    ),
                ),
                (
                    "uploaded",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Дата и время загрузки фотографии",
                        verbose_name="Загружена",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Дата и время последнего изменения фотографии",
                        verbose_name="Изменена",
                    ),
                ),
                (
                    "public",
                    models.BooleanField(
                        default=True,
                        help_text="Фотография публичная",
                        verbose_name="Публичная",
                    ),
                ),
                (
                    "album",
                    models.ForeignKey(
                        help_text="Альбом, в котором размещена фотография",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gallery.album",
                        verbose_name="Альбом",
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Тэги фотографии",
                        related_name="tag_photos",
                        to="gallery.tag",
                        verbose_name="Тэги",
                    ),
                ),
            ],
            options={
                "verbose_name": "Фотография",
                "verbose_name_plural": "Фотографии",
                "ordering": ["pk"],
            },
        ),
        migrations.AddField(
            model_name="album",
            name="cover",
            field=models.ForeignKey(
                blank=True,
                help_text="Обложка альбома",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="gallery.photo",
                verbose_name="Обложка",
            ),
        ),
        migrations.AddField(
            model_name="album",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                help_text="Тэги альбома",
                related_name="tag_albums",
                to="gallery.tag",
                verbose_name="Тэги",
            ),
        ),
    ]
