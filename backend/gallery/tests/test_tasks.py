"""Тесты фоновой генерации миниатюр и превью фотографий."""

import io
from typing import Any

from django.tasks import Task, TaskResult, task_backends
from django.tasks.backends.base import BaseTaskBackend
from django.tasks.signals import task_enqueued
from django.test import TestCase, TransactionTestCase, override_settings
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
    Существование кэш-файлов проверяется через storage.exists: обращение
    к bool, url или path кэш-файла запускает генерацию на месте
    (стратегия JustInTime) и маскирует сломанную задачу.
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

    def _cache_exists(self, cachefile: ImageCacheFile) -> bool:
        """Проверить существование кэш-файла в хранилище без генерации."""
        return cachefile.storage.exists(cachefile.name)

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
        self.assertTrue(self._cache_exists(photo.image_thumbnail))
        self.assertTrue(self._cache_exists(photo.image_preview))

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
        self.assertTrue(self._cache_exists(photo.image_thumbnail))
        self.assertTrue(self._cache_exists(photo.image_preview))

    def test_album_change_enqueues(self) -> None:
        """Смена альбома с перемещением файла порождает задачу."""
        photo = Photo.objects.get(pk=PhotoFactory().pk)
        target_album = Album.objects.create(name="Целевой альбом")
        self.enqueued.clear()
        photo.album = target_album
        photo.save()
        self.assertEqual(len(self.enqueued), 1)
        self.assertTrue(self._cache_exists(photo.image_thumbnail))
        self.assertTrue(self._cache_exists(photo.image_preview))

    def test_task_skips_missing_photo(self) -> None:
        """Задача для несуществующей фотографии завершается успехом."""
        deleted_pk = Photo.objects.get(pk=PhotoFactory().pk).pk + 100500
        result = generate_photo_images.enqueue(deleted_pk)
        self.assertEqual(result.status, "SUCCESSFUL")


class TestCacheFreshness(TransactionTestCase):
    """Актуальный кэш не перегенерируется, отсутствующий - создается заново."""

    def test_task_skips_fresh_cache(self) -> None:
        """Свежий кэш-файл задача не перезаписывает: время изменения сохраняется."""
        photo = Photo.objects.get(pk=PhotoFactory().pk)
        cachefile = photo.image_thumbnail
        mtime_before = cachefile.storage.get_modified_time(cachefile.name)

        generate_photo_images.enqueue(photo.pk)

        mtime_after = cachefile.storage.get_modified_time(cachefile.name)
        self.assertEqual(mtime_after, mtime_before)

    def test_task_regenerates_missing_cache(self) -> None:
        """Отсутствующий кэш-файл задача создает заново."""
        photo = Photo.objects.get(pk=PhotoFactory().pk)
        cachefile = photo.image_thumbnail
        cachefile.storage.delete(cachefile.name)
        self.assertFalse(cachefile.storage.exists(cachefile.name))

        generate_photo_images.enqueue(photo.pk)

        self.assertTrue(cachefile.storage.exists(cachefile.name))


class TestSignalSurvivesQueueFailure(TestCase):
    """Отказ постановки задачи не прерывает сохранение фотографии.

    Заглушка-бэкенд имитирует недоступную очередь: постановка задачи
    завершается ошибкой на границе сигнала, а сохранение фотографии
    и извлечение EXIF должны завершиться успешно.
    """

    def tearDown(self) -> None:
        """Вернуть обработчику задач исходную конфигурацию."""
        self._reset_handler()
        super().tearDown()

    @staticmethod
    def _reset_handler() -> None:
        """Сбросить кэш конфигурации обработчика задач."""
        task_backends._settings = None  # noqa: SLF001
        task_backends.__dict__.pop("settings", None)

    def test_save_succeeds_when_queue_unavailable(self) -> None:
        """Сохранение фотографии переживает ошибку постановки задачи."""
        self._reset_handler()
        self.addCleanup(self._reset_handler)
        with (
            override_settings(TASKS={"default": {"BACKEND": "gallery.tests.test_tasks.FailingTaskBackend"}}),
            self.assertLogs("gallery.signals", level="ERROR") as logs,
        ):
            photo = Photo.objects.get(pk=PhotoFactory().pk)

        self.assertTrue(Photo.objects.filter(pk=photo.pk).exists())
        self.assertTrue(any("Постановка задачи генерации" in message for message in logs.output))


class FailingTaskBackend(BaseTaskBackend):
    """Бэкенд, имитирующий недоступную очередь: постановка всегда отказывает."""

    def enqueue(self, task: Task, args: list[Any], kwargs: dict[str, Any]) -> TaskResult:  # noqa: ARG002
        """Отказать в постановке задачи."""
        msg = "Очередь фоновых задач недоступна"
        raise RuntimeError(msg)
