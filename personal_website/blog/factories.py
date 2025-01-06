"""Фабрики для генерации экземпляров классов с фейковыми данными для тестирования."""

import factory  # type: ignore[import-untyped]
from django.utils.timezone import now

from accounts.factories import UserFactory
from blog.models import Article, Category, Comment, Series, Topic


class CategoryFactory(factory.django.DjangoModelFactory):
    """Фабрика для генерации случайных данных для модели Category."""

    class Meta:  # noqa: D106
        model = Category

    name = factory.Faker("word")
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

    name = factory.Faker("word")
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

    name = factory.Faker("word")
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

    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    content = factory.Faker("text")
    published_at = factory.LazyFunction(now)
    modified_at = factory.LazyFunction(now)
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


class CommentFactory(factory.django.DjangoModelFactory):
    """Фабрика для генерации объектов комментариев к статьям."""

    class Meta:  # noqa: D106
        model = Comment

    article = factory.SubFactory(ArticleFactory)
    author = factory.SubFactory(UserFactory)
    content = factory.Faker("text")
    posted = factory.LazyFunction(now)

    def __new__(cls, *args, **kwargs) -> "Comment":
        """Возвращается объект Comment."""
        return super().__new__(*args, **kwargs)
