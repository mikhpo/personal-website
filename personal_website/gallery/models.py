"""Модели галереи."""
from datetime import datetime
from pathlib import Path
from typing import Self

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.timezone import get_current_timezone, now
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from PIL import Image as pImage
from PIL.ExifTags import TAGS

from gallery.managers import PublicAlbumManager, PublicPhotoManager
from gallery.utils import move_photo_image, photo_image_upload_path
from personal_website.storages import select_storage
from personal_website.utils import get_unique_slug

thumbnail_size: int = settings.GALLERY_THUMBNAIL_SIZE
preview_size: int = settings.GALLERY_PREVIEW_SIZE
resize_quality: int = settings.GALLERY_RESIZE_QUALITY

current_timezone = get_current_timezone()


class Tag(models.Model):
    """Тэг для фотографий и альбомов."""

    name = models.CharField(verbose_name="Наименование", max_length=255, help_text="Наименование тэга")
    slug = models.SlugField(verbose_name="Слаг", unique=True, blank=True, help_text="Слаг тэга")
    description = models.TextField(verbose_name="Описание", blank=True, help_text="Описание тэга")

    class Meta:  # noqa: D106
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
        ordering = ("slug",)

    def __str__(self) -> str:
        """Строковое представление тэга представляет собой имя тэга."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Если слаг не указан, то автоматически определить слаг."""
        if not self.slug:
            self.slug = get_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Абсолютная ссылка на тэг определяется по слагу тэга."""
        return reverse("gallery:tag-detail", kwargs={"slug": self.slug})


class Album(models.Model):
    """Модель альбома с фотографиями."""

    name = models.CharField(verbose_name="Наименование", max_length=255, help_text="Наименование альбома")
    description = models.TextField(verbose_name="Описание", blank=True, help_text="Описание альбома")
    slug = models.SlugField(verbose_name="Слаг", blank=True, unique=True, help_text="Слаг альбома")
    created_at = models.DateTimeField(
        verbose_name="Создан",
        auto_now_add=True,
        help_text="Дата и время создания альбома",
    )
    updated_at = models.DateTimeField(
        verbose_name="Обновлен",
        auto_now=True,
        help_text="Дата и время последнего обновления альбома",
    )
    public = models.BooleanField(verbose_name="Публичный", default=True, help_text="Альбом публичный")
    cover = models.OneToOneField(
        "Photo",
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Обложка",
        null=True,
        blank=True,
        help_text="Обложка альбома",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        blank=True,
        related_name="tag_albums",
        help_text="Тэги альбома",
    )
    order = models.PositiveIntegerField(
        verbose_name="Порядок",
        default=0,
        blank=False,
        null=False,
    )

    objects = models.Manager()
    published = PublicAlbumManager()

    class Meta:  # noqa: D106
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"
        ordering = ("-order",)

    def __str__(self) -> str:
        """Строкое представление альбома является названием альбома."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Если слаг альбома не указан, то слаг определяется автоматически по имени альбома."""
        if not self.slug:
            self.slug = get_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Абсолютная ссылка на альбом определяется слагом альбома."""
        return reverse("gallery:album-detail", kwargs={"slug": self.slug})

    @property
    def photos_count(self) -> int:
        """Количество фотографий в альбоме."""
        photos = Photo.objects.filter(album=self)
        return photos.count()

    @property
    def public_photos_count(self) -> int:
        """Количество публичных фотографий в альбоме."""
        photos = Photo.published.filter(album=self)
        return photos.count()


class Photo(models.Model):
    """Модель фотографии."""

    image = models.ImageField(
        verbose_name="Изображение",
        upload_to=photo_image_upload_path,
        storage=select_storage,
        max_length=255,
    )
    name = models.CharField(
        verbose_name="Наименование",
        blank=True,
        max_length=255,
        help_text="Наименование фотографии",
    )
    description = models.TextField(verbose_name="Описание", blank=True, help_text="Описание фотографии")
    slug = models.SlugField(verbose_name="Слаг", blank=True, unique=True, help_text="Слаг фотографии")
    uploaded_at = models.DateTimeField(
        verbose_name="Загружена",
        auto_now_add=True,
        help_text="Дата и время загрузки фотографии",
    )
    modified_at = models.DateTimeField(
        verbose_name="Изменена",
        auto_now=True,
        help_text="Дата и время последнего изменения фотографии",
    )
    public = models.BooleanField(verbose_name="Публичная", default=True, help_text="Фотография публичная")
    album = models.ForeignKey(
        Album,
        verbose_name="Альбом",
        on_delete=models.CASCADE,
        help_text="Альбом, в котором размещена фотография",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        blank=True,
        related_name="tag_photos",
        help_text="Тэги фотографии",
    )
    image_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFit(height=thumbnail_size, width=thumbnail_size)],
        format="JPEG",
        options={"quality": resize_quality},
    )
    image_preview = ImageSpecField(
        source="image",
        processors=[ResizeToFit(width=preview_size, height=preview_size)],
        format="JPEG",
        options={"quality": resize_quality},
    )

    objects = models.Manager()
    published = PublicPhotoManager()

    class Meta:  # noqa: D106
        ordering = ("pk",)
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"

    def __str__(self) -> str:
        """Строковое представление фотографии является наименованием фотографии."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Операции, выполняемые при каждом сохранении модели.

        - Если был изменен альбом фотографии, то изменяется адрес хранения фотографии.
        - Если у фотографии не указано название, то получить его из имени файла.
        - Если у фотографии не указан слаг, то определить его из названия.
        """
        if self.pk:
            previous = Photo.objects.get(pk=self.pk)
            if previous.album != self.album:
                self.change_album_photo_image_path(previous)
        if not self.name:
            self.name = Path(self.image.name).stem
        if not self.slug:
            self.slug = get_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Абсолютная ссылка на фотографию определяется слагом фотографии."""
        return reverse("gallery:photo-detail", kwargs={"slug": self.slug})

    @cached_property
    def exif(self) -> dict:
        """Получить данные EXIF при помощи библиотеки PIL."""
        exif_data = {}
        storage = select_storage()
        if storage.exists(self.image.name):
            with pImage.open(self.image) as img:
                if hasattr(img, "_getexif"):
                    info = img._getexif()  # noqa: SLF001
                    if not info:
                        return {}
                    for tag, value in info.items():
                        decoded = TAGS.get(tag, tag)
                        exif_data[decoded] = value
                img.close()
        return exif_data

    @cached_property
    def camera_manufacturer(self) -> str:
        """Производитель камеры."""
        return self.exif.get("Make", "")

    @cached_property
    def camera_model(self) -> str:
        """Модель камеры."""
        manufacturer = self.camera_manufacturer
        model = self.exif.get("Model", "")
        if manufacturer in model:
            model = model.replace(manufacturer, "")
            return model.strip()
        return ""

    @cached_property
    def camera(self) -> str:
        """Название камеры = производитель + модель."""
        if self.camera_model:
            return f"{self.camera_manufacturer} {self.camera_model}"
        return self.camera_manufacturer

    @cached_property
    def lens_model(self) -> str:
        """Модель объектива."""
        return self.exif.get("LensModel", "")

    @cached_property
    def aperture(self) -> int | None:
        """Диафрагменное число."""
        aperture = self.exif.get("FNumber", None)
        if aperture:
            return int(aperture)
        return None

    @cached_property
    def exposure(self) -> str:
        """Выдержка."""
        if "ExposureTime" in self.exif:
            exposure_time: float = self.exif["ExposureTime"]
            if exposure_time <= 1:
                numenator = exposure_time.numerator
                denominator = exposure_time.denominator
                return f"{numenator}/{denominator}"
            return str(int(exposure_time))
        return ""

    @cached_property
    def iso(self) -> int | None:
        """Светочувствительность."""
        iso = self.exif.get("ISOSpeedRatings", None)
        if iso:
            return int(iso)
        return None

    @cached_property
    def focal_length(self) -> int | None:
        """Фокусное расстояние."""
        focal_length = self.exif.get("FocalLength", None)
        if focal_length:
            return int(focal_length)
        return None

    @cached_property
    def datetime_taken(self) -> datetime:
        """Получить время съемки фотографии из EXIF или использовать время создания файла."""
        # Проверить наличие файла изображения.
        if not self.image.name or not Path(self.image.path).exists():
            return now()

        # Получить дату и время последнего изменения файла.
        time_stamp = Path(self.image.path).stat().st_mtime
        date_time = datetime.fromtimestamp(time_stamp, current_timezone)

        # Если в EXIF отсутствует дата и время съемки,
        # то вернуть дату и время последнего изменения.
        original_exif = self.exif.get("DateTimeOriginal")
        if not original_exif:
            return date_time

        # Получить дату и время съемки из EXIF, если не перехвачено исключение.
        # Если перехвачено исключение, то вернуть дату и время изменения файла.
        try:
            return datetime.strptime(original_exif, "%Y:%m:%d %H:%M:%S")  # noqa: DTZ007
        except ValueError:
            return date_time

    def change_album_photo_image_path(self, previous: Self) -> Self:
        """Изменить местоположение изображения фотографии относительно альбома."""
        old_path = previous.image.path
        new_path = move_photo_image(self, old_path)
        file_name = Path(new_path).name
        new_relative_path = photo_image_upload_path(self, file_name)
        self.image = new_relative_path
        return self
