"""Фабрики для генерации экземпляров классов с фейковыми данными для тестирования."""
import factory

from blog.models import Category, Series, Topic


class CategoryFactory(factory.django.DjangoModelFactory):
    """Фабрика для генерации случайных данных для модели Category."""

    class Meta:  # noqa: D106
        model = Category

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    slug = factory.LazyAttribute(lambda _: None)
    image = factory.django.ImageField()
    public = factory.Faker("boolean")

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
    public = factory.Faker("boolean")

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
    public = factory.Faker("boolean")

    def __new__(cls, *args, **kwargs) -> "Series":
        """Возвращается объект Series."""
        return super().__new__(*args, **kwargs)
