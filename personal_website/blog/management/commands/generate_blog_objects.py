"""Команда управления Django для генерации тестовых объектов блога.

Создает тестовые данные для проверки пагинации блога, включая:
- Пользователей (авторов статей)
- Категории статей
- Серии статей
- Темы статей
- Статьи с привязкой к созданным категориям, сериям и темам

Использует фабрики моделей для генерации тестовых данных.
"""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from accounts.factories import UserFactory
from blog.factories import ArticleFactory, CategoryFactory, SeriesFactory, TopicFactory


class Command(BaseCommand):
    """Команда для генерации тестовых объектов блога."""

    help = "Генерация тестовых объектов для проверки пагинации блога"

    def add_arguments(self, parser: CommandParser) -> None:
        """Добавляет аргументы команды для настройки количества создаваемых объектов."""
        parser.add_argument(
            "--articles",
            type=int,
            default=20,
            help="Количество статей для создания (по умолчанию: 20)",
        )
        parser.add_argument(
            "--categories",
            type=int,
            default=5,
            help="Количество категорий для создания (по умолчанию: 5)",
        )
        parser.add_argument(
            "--series",
            type=int,
            default=3,
            help="Количество серий для создания (по умолчанию: 3)",
        )
        parser.add_argument(
            "--topics",
            type=int,
            default=7,
            help="Количество тем для создания (по умолчанию: 7)",
        )

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ANN401, ARG002
        """Выполняет основную логику команды по генерации тестовых объектов.

        Создает пользователей, категории, серии, темы и статьи в заданном количестве.
        Выводит информацию о процессе создания объектов в стандартный вывод.

        Args:
            *args: Позиционные аргументы команды (не используются)
            **options: Именованные аргументы команды, включая:
                - articles (int): Количество статей для создания
                - categories (int): Количество категорий для создания
                - series (int): Количество серий для создания
                - topics (int): Количество тем для создания
        """
        # Создание пользователей
        self.stdout.write("Создание пользователей...")
        user = UserFactory()

        # Создание категорий, серий и тем блога
        self.stdout.write("Создание категорий блога...")
        categories = CategoryFactory.create_batch(options["categories"])

        self.stdout.write("Создание серий блога...")
        series = SeriesFactory.create_batch(options["series"])

        self.stdout.write("Создание тем блога...")
        topics = TopicFactory.create_batch(options["topics"])

        # Создание статей
        articles_count = options["articles"]
        self.stdout.write(f"Создание {articles_count} статей...")
        articles = ArticleFactory.create_batch(
            articles_count,
            author=user,
            categories=categories[:2],
            series=series[:1],
            topics=topics[:3],
        )
        self.stdout.write(f"Создано {len(articles)} статей")

        self.stdout.write(
            self.style.SUCCESS(
                f"Успешно сгенерированы тестовые объекты для блога: {len(articles)} статей",
            ),
        )
