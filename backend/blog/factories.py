"""Фабрики для генерации экземпляров классов с фейковыми данными для тестирования."""

import factory  # type: ignore[import-untyped]
from django.utils.timezone import now
from faker import Faker

from accounts.factories import UserFactory
from blog.models import Article, Category, Comment, Series, Topic

fake = Faker(locale="ru_RU")


class CategoryFactory(factory.django.DjangoModelFactory):
    """Фабрика для генерации случайных данных для модели Category."""

    class Meta:  # noqa: D106
        model = Category
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"{fake.word()}_{n}")
    description = factory.Faker("sentence")
    slug = factory.LazyAttribute(lambda _: None)
    image = factory.django.ImageField()
    public = factory.LazyAttribute(lambda _: True)

    def __new__(cls, *args, **kwargs) -> "Category":
        """Возвращается объект Category."""
        return super().__new__(*args, **kwargs)


class TopicFactory(factory.django.DjangoModelFactory):
    """Фабрика для генерации случайных данных для модели Topic."""

    class Meta:  # noqa: D106
        model = Topic
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"{fake.word()}_{n}")
    description = factory.Faker("sentence")
    slug = factory.LazyAttribute(lambda _: None)
    image = factory.django.ImageField()
    public = factory.LazyAttribute(lambda _: True)

    def __new__(cls, *args, **kwargs) -> "Topic":
        """Возвращается объект Topic."""
        return super().__new__(*args, **kwargs)


class SeriesFactory(factory.django.DjangoModelFactory):
    """Фабрика для генерации случайных данных для модели Series."""

    class Meta:  # noqa: D106
        model = Series
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"{fake.word()}_{n}")
    description = factory.Faker("sentence")
    slug = factory.LazyAttribute(lambda _: None)
    image = factory.django.ImageField()
    public = factory.LazyAttribute(lambda _: True)

    def __new__(cls, *args, **kwargs) -> "Series":
        """Возвращается объект Series."""
        return super().__new__(*args, **kwargs)


class ArticleFactory(factory.django.DjangoModelFactory):
    """Фабрика для генерации случайных данных для модели Article."""

    class Meta:  # noqa: D106
        model = Article
        skip_postgeneration_save = True
        django_get_or_create = ("title",)

    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    content = factory.LazyAttribute(lambda _: generate_article_content())
    published_at = factory.LazyAttribute(lambda _: now())
    modified_at = factory.LazyAttribute(lambda _: now())
    slug = factory.LazyAttribute(lambda _: None)
    image = factory.django.ImageField()
    public = factory.LazyAttribute(lambda _: True)
    author = factory.SubFactory(UserFactory)

    @factory.post_generation
    def series(self, create, extracted, **kwargs) -> None:  # noqa: ARG002, ANN001
        """Добавить серии статьи.

        Если класс фабрики вызывается как ArticleFactory() или вызывается метод ArticleFactory.build(),
        то серии не добавляются. Если вызывается метод фабрики ArticleFactory.create(),
        то аргументу series можно передать последовательность объектов серий.
        """
        if not create or not extracted:
            return
        self.series.add(*extracted)

    @factory.post_generation
    def topics(self, create, extracted, **kwargs) -> None:  # noqa: ARG002, ANN001
        """Добавить темы статьи.

        Если класс фабрики вызывается как ArticleFactory() или вызывается метод ArticleFactory.build(),
        то темы не добавляются. Если вызывается метод фабрики ArticleFactory.create(),
        то аргументу topics можно передать последовательность объектов тем.
        """
        if not create or not extracted:
            return
        self.topics.add(*extracted)

    @factory.post_generation
    def categories(self, create, extracted, **kwargs) -> None:  # noqa: ARG002, ANN001
        """Добавить категории статьи.

        Если класс фабрики вызывается как ArticleFactory() или вызывается метод ArticleFactory.build(),
        то категории не добавляются. Если вызывается метод фабрики ArticleFactory.create(),
        то аргументу categories можно передать последовательность объектов тем.
        """
        if not create or not extracted:
            return
        self.categories.add(*extracted)

    def __new__(cls, *args, **kwargs) -> "Article":
        """Возвращается объект Article."""
        return super().__new__(*args, **kwargs)


def generate_article_content() -> str:
    """Генерирует HTML-контент статьи с переменной длиной.

    Возвращает HTML-контент статьи разной длины:
    - 30% статей: короткий контент (~100 слов)
    - 50% статей: средний контент (~300 слов)
    - 20% статей: длинный контент (~500 слов)
    """
    # Определяем длину контента (30% короткий, 50% средний, 20% длинный)
    content_length = fake.random_element([0.1, 0.5, 0.9])
    short_threshold = 0.3  # 30% для короткого контента
    medium_threshold = 0.8  # 80% для среднего контента (30% + 50%)

    if content_length < short_threshold:
        word_count = fake.random_int(100, 120)
    elif content_length < medium_threshold:
        word_count = fake.random_int(250, 350)
    else:
        word_count = fake.random_int(450, 550)

    # Генерируем HTML-контент из абзацев
    words = fake.words(nb=word_count)
    paragraphs = []

    # Разбиваем слова на абзацы по 30-50 слов
    i = 0
    while i < len(words):
        paragraph_length = fake.random_int(30, 50)
        paragraph_words = words[i : i + paragraph_length]
        paragraphs.append(f"<p>{' '.join(paragraph_words)}</p>")
        i += paragraph_length

    return "".join(paragraphs)


class CommentFactory(factory.django.DjangoModelFactory):
    """Фабрика для генерации объектов комментариев к статьям."""

    class Meta:  # noqa: D106
        model = Comment

    article = factory.SubFactory(ArticleFactory)
    author = factory.SubFactory(UserFactory)
    content = factory.Faker("text")
    posted = factory.LazyAttribute(lambda _: now())

    def __new__(cls, *args, **kwargs) -> "Comment":
        """Возвращается объект Comment."""
        return super().__new__(*args, **kwargs)
