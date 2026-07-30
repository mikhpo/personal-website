"""Модели галереи."""

import io
import logging
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Self

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.timezone import get_current_timezone, is_aware, make_naive, now
from imagekit.models import ImageSpecField  # type: ignore[import-untyped]
from imagekit.processors import ResizeToFit  # type: ignore[import-untyped]
from PIL import Image as pImage
from PIL.ExifTags import TAGS
from PIL.TiffImagePlugin import IFDRational

from gallery.managers import PublicAlbumManager, PublicPhotoManager
from gallery.utils import compute_datetime_taken, exif_value_to_json, move_photo_image, photo_image_upload_path
from personal_website.storages import StorageType, select_storage
from personal_website.utils import get_unique_slug

thumbnail_size: int = settings.GALLERY_THUMBNAIL_SIZE
preview_size: int = settings.GALLERY_PREVIEW_SIZE
resize_quality: int = settings.GALLERY_RESIZE_QUALITY

current_timezone = get_current_timezone()
storage: StorageType = select_storage()
logger = logging.getLogger(__name__)


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
        ordering = ("-order", "-created_at")

    def __str__(self) -> str:
        """Строкое представление альбома является названием альбома."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Если слаг альбома не указан, то слаг определяется автоматически по имени альбома."""
        if not self.slug:
            self.slug = get_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Абсолютная ссылка на альбом определяется первичным ключом альбома."""
        return reverse("gallery:album-detail", kwargs={"pk": self.pk})

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
    taken_at = models.DateTimeField(
        verbose_name="Создана",
        null=False,
        blank=False,
        help_text="Дата и время съемки фотографии",
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
        related_name="photos",
        help_text="Альбом, в котором размещена фотография",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        blank=True,
        related_name="tag_photos",
        help_text="Тэги фотографии",
    )
    exif = models.JSONField(
        verbose_name="EXIF данные",
        null=True,
        blank=True,
        default=dict,
        editable=False,
        help_text="EXIF данные изображения",
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
        ordering = ("-taken_at",)
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"

    def __str__(self) -> str:
        """Строковое представление фотографии является наименованием фотографии."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Операции, выполняемые при каждом сохранении модели.

        - Сохраняет EXIF данные в поле exif при изменении изображения.
        - Вычисляет taken_at если изображение изменилось или для нового экземпляра.
        - Если был изменен альбом фотографии, то изменяется адрес хранения фотографии.
        - Если у фотографии не указано название, то получить его из имени файла.
        - Если у фотографии не указан слаг, то определить его из названия.
        """
        # При частичном сохранении (update_fields) EXIF не пересчитывается.
        update_fields = kwargs.get("update_fields")
        needs_exif_update = update_fields is None and self.should_update_taken_at()

        # taken_at имеет ограничение null=False, поэтому при первом сохранении
        # нужно временное значение. Точное значение вычисляется после super().save(),
        # когда файл уже находится в хранилище.
        if needs_exif_update:
            self.taken_at = now()

        if self.pk:
            previous = Photo.objects.get(pk=self.pk)
            if previous.album != self.album:
                self.change_album_photo_image_path(previous)
        if not self.name:
            self.name = storage.stem(self.image.name)
        if not self.slug:
            self.slug = get_unique_slug(self, self.name)
        super().save(*args, **kwargs)

        # После super().save() файл находится в хранилище — можно извлечь EXIF.
        if needs_exif_update:
            self.exif = self._extract_exif_from_image()
            self.taken_at = compute_datetime_taken(self)
            super().save(update_fields=["exif", "taken_at"])

    def get_absolute_url(self) -> str:
        """Абсолютная ссылка на фотографию определяется первичным ключом фотографии."""
        return reverse("gallery:photo-detail", kwargs={"pk": self.pk})

    def should_update_taken_at(self) -> bool:
        """Проверить, нужно ли обновить поле taken_at.

        Returns:
            True если поле нужно обновить, False в противном случае.
        """
        # Новый экземпляр - всегда вычисляем
        if not self.pk:
            return True

        # Проверяем изменилось ли изображение
        try:
            prev = Photo.objects.get(pk=self.pk)

            # Разные файлы - нужно обновить
            if prev.image.name != self.image.name:
                return True

            # То же имя файла - проверяем modification time
            current_mtime = storage.get_modified_time(self.image.name)
            previous_mtime = storage.get_modified_time(prev.image.name)
            return current_mtime != previous_mtime

        except Photo.DoesNotExist:
            return True
        else:
            return False

    def _extract_exif_from_image(self) -> dict:
        """Извлечь данные EXIF из файла изображения в JSON-совместимый словарь.

        Метод читает файл изображения через хранилище и извлекает EXIF данные
        с помощью PIL. Значения преобразуются к JSON-совместимым типам для
        сохранения в поле exif.

        Returns:
            Словарь EXIF данных с человекочитаемыми ключами тегов.
        """
        exif_data: dict = {}
        if self.image and self.image.name and self.image.storage.exists(self.image.name):
            try:
                img_bytes = self.image.storage.read_bytes(self.image.name)
                with pImage.open(io.BytesIO(img_bytes)) as img:
                    if hasattr(img, "_getexif"):
                        info = img._getexif()  # noqa: SLF001
                        if info:
                            for tag, value in info.items():
                                decoded = TAGS.get(tag, tag)
                                json_value = exif_value_to_json(value)
                                if json_value is not None:
                                    exif_data[decoded] = json_value
            except (FileNotFoundError, PermissionError, OSError):
                logger.exception("Ошибка чтения файла %s", self.image.name)
        return exif_data

    @cached_property
    def camera_manufacturer(self) -> str:
        """Производитель камеры."""
        return (self.exif or {}).get("Make", "")

    @cached_property
    def camera_model(self) -> str:
        """Модель камеры."""
        manufacturer = self.camera_manufacturer
        model: str = (self.exif or {}).get("Model", "")
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
        return (self.exif or {}).get("LensModel", "")

    @cached_property
    def aperture(self) -> str | None:
        """Диафрагменное число."""
        if f_number := (self.exif or {}).get("FNumber", None):
            aperture = float(f_number)
            formatted_aperture = int(aperture) if aperture.is_integer() else round(aperture, 2)
            return f"F/{formatted_aperture}"
        return None

    @cached_property
    def exposure(self) -> str:
        """Возвращает значение выдержки из метаданных EXIF.

        Значение выдержки может быть получено либо напрямую из PIL (IFDRational),
        либо из JSONField (float). В обоих случаях выполняется форматирование
        в строку вида "numerator/denominator".

        - Для IFDRational используются numerator и denominator напрямую.
        - Для float-значений <= 1 применяется Fraction с ограничением знаменателя
          для получения человекочитаемой дроби (например, 0.004 -> 1/250).
        - Для значений > 1 возвращается целочисленное представление.

        Returns:
            Строка с выдержкой или пустая строка, если ключ отсутствует.
        """
        exif = self.exif or {}
        if "ExposureTime" in exif:
            exposure_time: float | IFDRational = exif["ExposureTime"]
            if isinstance(exposure_time, IFDRational):
                numenator = exposure_time.numerator
                denominator = exposure_time.denominator
            elif isinstance(exposure_time, (int, float)):
                if exposure_time <= 1:
                    frac = Fraction(exposure_time).limit_denominator(10000)
                    return f"{frac.numerator}/{frac.denominator}"
                return str(int(exposure_time))
            else:
                return str(exposure_time)
            return f"{numenator}/{denominator}"
        return ""

    @cached_property
    def iso(self) -> int | None:
        """Светочувствительность."""
        if iso := (self.exif or {}).get("ISOSpeedRatings", None):
            return int(iso)
        return None

    @cached_property
    def focal_length(self) -> int | None:
        """Фокусное расстояние."""
        if focal_length := (self.exif or {}).get("FocalLength", None):
            return int(focal_length)
        return None

    @cached_property
    def datetime_taken(self) -> datetime:
        """Получить время съемки фотографии из EXIF или использовать время создания файла.

        EXIF данные DateTimeOriginal не содержат информацию о часовом поясе.
        Для корректной сортировки фотографий все datetime объекты должны быть
        одного типа. Используем naive datetime (без часового пояса), поскольку
        невозможно определить часовой пояс места съемки.

        Время изменения файла, получаемое из хранилища, может быть timezone-aware
        (при USE_TZ=True). Для корректного преобразования aware datetime в naive
        используется timezone.make_naive(), который переводит время в текущий
        часовой пояс перед удалением информации о нём.
        """
        # Проверить наличие файла изображения.
        if not self.image.name or not storage.exists(self.image.name):
            return now()

        # Получить дату и время последнего изменения файла и преобразовать
        # timezone-aware datetime в naive с учётом текущего часового пояса.
        modified_time = storage.get_modified_time(self.image.name)
        date_time = make_naive(modified_time) if is_aware(modified_time) else modified_time

        # Если в EXIF отсутствует дата и время съемки,
        # то вернуть дату и время последнего изменения.
        original_exif = (self.exif or {}).get("DateTimeOriginal")
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
