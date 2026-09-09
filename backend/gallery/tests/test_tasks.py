"""Тесты фоновой генерации миниатюр и превью фотографий."""

import io

from django.tasks import TaskResult, task_backends
from django.tasks.signals import task_enqueued
from django.test import TestCase
from imagekit.cachefiles import ImageCacheFile
from PIL import Image as pImage

from gallery.factories import PhotoFactory, generate_image_with_exif
from gallery.models import Album, Photo
from gallery.tasks import generate_photo_images
from personal_website import settings


class TestPhotoImageGeneration(TestCase):
    """Генерация миниатюры и превью ставится задачей после сохранения фотографии.

    В тестах задачи выполняются инлайн через ImmediateBackend, поэтому
    после сохранения фотографии кэш-файлы уже присутствуют в хранилище.
    """

    def setUp(self) -> None:
        """Подключить приемник сигнала постановки задач.

        weak=False обязателен: по умолчанию диспетчер сигналов хранит
        приемники слабыми ссылками, и приемник теряется до отправки сигнала.
        """
        self.enqueued: list[TaskResult] = []
        task_enqueued.connect(self._record_task, dispatch_uid="test-task-enqueued", weak=False)
        self.addCleanup(task_enqueued.disconnect, dispatch_uid="test-task-enqueued")

    def _record_task(self, sender: type[Photo], task_result: TaskResult, **kwargs) -> None:  # noqa: ARG002
        """Запомнить постановку задачи генерации изображений."""
        if task_result.task.module_path == generate_photo_images.module_path:
            self.enqueued.append(task_result)

    def _read_generated_image(self, cachefile: ImageCacheFile) -> pImage.Image:
        """Прочитать сгенерированный кэш-файл из хранилища как изображение."""
        data = cachefile.storage.read_bytes(cachefile.name)
        return pImage.open(io.BytesIO(data))

    def test_immediate_backend_selected_in_tests(self) -> None:
        """В тестовом окружении задачи выполняются встроенным ImmediateBackend."""
        self.assertEqual(task_backends["default"].__class__.__name__, "ImmediateBackend")

    def test_images_generated_on_create(self) -> None:
        """Создание фотографии порождает задачу: миниатюра и превью существуют."""
        photo = Photo.objects.get(pk=PhotoFactory().pk)
        self.assertEqual(len(self.enqueued), 1)
        self.assertTrue(photo.image_thumbnail)
        self.assertTrue(photo.image_preview)

        thumbnail = self._read_generated_image(photo.image_thumbnail)
        self.assertEqual(thumbnail.format, "JPEG")
        self.assertLessEqual(max(thumbnail.size), settings.GALLERY_THUMBNAIL_SIZE)

        preview = self._read_generated_image(photo.image_preview)
        self.assertEqual(preview.format, "JPEG")
        self.assertLessEqual(max(preview.size), settings.GALLERY_PREVIEW_SIZE)

    def test_exif_partial_save_does_not_enqueue(self) -> None:
        """Частичное сохранение EXIF и taken_at задачу не порождает."""
        photo = Photo.objects.get(pk=PhotoFactory().pk)
        self.enqueued.clear()
        photo.save(update_fields=["exif", "taken_at"])
        self.assertEqual(len(self.enqueued), 0)

    def test_name_partial_save_does_not_enqueue(self) -> None:
        """Частичное сохранение названия задачу не порождает."""
        photo = Photo.objects.get(pk=PhotoFactory().pk)
        self.enqueued.clear()
        photo.save(update_fields=["name"])
        self.assertEqual(len(self.enqueued), 0)

    def test_full_save_enqueues(self) -> None:
        """Полное сохранение фотографии порождает задачу."""
        photo = Photo.objects.get(pk=PhotoFactory().pk)
        self.enqueued.clear()
        photo.name = "Измененное название"
        photo.save()
        self.assertEqual(len(self.enqueued), 1)

    def test_image_replacement_enqueues(self) -> None:
        """Замена изображения порождает задачу и перегенерирует кэш-файлы."""
        photo = Photo.objects.get(pk=PhotoFactory().pk)
        self.enqueued.clear()
        photo.image = generate_image_with_exif()
        photo.save()
        self.assertEqual(len(self.enqueued), 1)
        self.assertTrue(photo.image_thumbnail)
        self.assertTrue(photo.image_preview)

    def test_album_change_enqueues(self) -> None:
        """Смена альбома с перемещением файла порождает задачу."""
        photo = Photo.objects.get(pk=PhotoFactory().pk)
        target_album = Album.objects.create(name="Целевой альбом")
        self.enqueued.clear()
        photo.album = target_album
        photo.save()
        self.assertEqual(len(self.enqueued), 1)
        self.assertTrue(photo.image_thumbnail)
        self.assertTrue(photo.image_preview)

    def test_task_skips_missing_photo(self) -> None:
        """Задача для несуществующей фотографии завершается успехом."""
        deleted_pk = Photo.objects.get(pk=PhotoFactory().pk).pk + 100500
        result = generate_photo_images.enqueue(deleted_pk)
        self.assertEqual(result.status, "SUCCESSFUL")
