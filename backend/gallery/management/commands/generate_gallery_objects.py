"""Команда управления Django для генерации тестовых объектов галереи.

Создает тестовые данные для проверки пагинации галереи, включая:
- Теги фотографий
- Альбомы фотографий
- Фотографии с привязкой к альбомам и тегам

Использует фабрики моделей для генерации тестовых данных.
"""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from faker import Faker

from gallery.factories import AlbumFactory, PhotoFactory, TagFactory

fake = Faker(locale="ru_RU")


class Command(BaseCommand):
    """Генерация тестовых объектов для проверки пагинации галереи."""

    help = "Генерация тестовых объектов для проверки пагинации галереи"

    def add_arguments(self, parser: CommandParser) -> None:
        """Добавление аргументов команды."""
        parser.add_argument(
            "--photos",
            type=int,
            default=50,
            help="Количество фотографий для создания (по умолчанию: 50)",
        )
        parser.add_argument(
            "--albums",
            type=int,
            default=3,
            help="Количество альбомов для создания (по умолчанию: 3)",
        )
        parser.add_argument(
            "--tags",
            type=int,
            default=5,
            help="Количество тегов для создания (по умолчанию: 5)",
        )

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ANN401, ARG002
        """Выполняет основную логику команды по генерации тестовых объектов.

        Создает теги, альбомы и фотографии в заданном количестве.
        Выводит информацию о процессе создания объектов в стандартный вывод.

        Args:
            *args: Позиционные аргументы команды (не используются)
            **options: Именованные аргументы команды, включая:
                - photos (int): Количество фотографий для создания
                - albums (int): Количество альбомов для создания
                - tags (int): Количество тегов для создания
        """
        # Создание тегов галереи
        self.stdout.write("Создание тегов галереи...")
        tags = TagFactory.create_batch(options["tags"])

        # Создание альбомов галереи
        self.stdout.write("Создание альбомов галереи...")
        albums = AlbumFactory.create_batch(options["albums"])

        # Создание фотографий
        photos_count = options["photos"]
        self.stdout.write(f"Создание {photos_count} фотографий...")

        photos = []
        for _ in range(photos_count):
            photo = PhotoFactory.create(
                album=fake.random_element(albums),
                tags=fake.random_elements(tags, length=fake.random_int(1, len(tags)), unique=True),
            )
            photos.append(photo)
        self.stdout.write(f"Создано {len(photos)} фотографий")

        self.stdout.write(
            self.style.SUCCESS(
                f"Успешно сгенерированы тестовые объекты для галереи: {len(photos)} фотографий",
            ),
        )
