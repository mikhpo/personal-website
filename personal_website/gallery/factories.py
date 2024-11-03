"""Фабрики для генерации объектов галереи со случайными данными."""
import factory
from django.utils.timezone import now

from gallery.models import Album, Photo, Tag


class TagFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания объектов Tag."""

    class Meta:  # noqa: D106
        model = Tag

    name = factory.Faker("word")
    slug = factory.LazyAttribute(lambda _: None)
    description = factory.Faker("sentence")

    def __new__(cls, *args, **kwargs) -> "Tag":
        """Возвращается объект Tag."""
        return super().__new__(*args, **kwargs)


class AlbumFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания объектов Album."""

    class Meta:  # noqa: D106
        model = Album
        skip_postgeneration_save = True

    name = factory.Faker("sentence")
    description = factory.Faker("text")
    slug = factory.LazyAttribute(lambda _: None)
    created_at = factory.LazyFunction(now)
    updated_at = factory.LazyFunction(now)
    public = factory.Faker("pybool")
    cover = factory.LazyAttribute(lambda _: None)
    order = factory.Sequence(lambda n: n + 1)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs) -> None:  # noqa: ARG002, ANN001
        """Добавить тэги альбома.

        Если класс фабрики вызывается как AlbumFactory() или вызывается метод AlbumFactory.build(),
        то тэги не добавляются. Если вызывается метод фабрики AlbumFactory.create(),
        то аргументу tags можно передать последовательность объектов тэгов.
        """
        if not create or not extracted:
            return
        self.tags.add(*extracted)

    def __new__(cls, *args, **kwargs) -> "Album":
        """Возвращается объект Album."""
        return super().__new__(*args, **kwargs)


class PhotoFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания объектов Photo."""

    class Meta:  # noqa: D106
        model = Photo
        skip_postgeneration_save = True

    image = factory.django.ImageField()
    name = factory.Faker("word")
    description = factory.Faker("sentence")
    slug = factory.LazyAttribute(lambda _: None)
    uploaded_at = factory.LazyFunction(now)
    modified_at = factory.LazyFunction(now)
    public = factory.Faker("pybool")
    album = factory.SubFactory(AlbumFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs) -> None:  # noqa: ARG002, ANN001
        """Добавить тэги фотографии.

        Если класс фабрики вызывается как PhotoFactory() или вызывается метод PhotoFactory.build(),
        то тэги не добавляются. Если вызывается метод фабрики PhotoFactory.create(),
        то аргументу tags можно передать последовательность объектов тэгов.
        """
        if not create or not extracted:
            return
        self.tags.add(*extracted)

    def __new__(cls, *args, **kwargs) -> "Photo":
        """Возвращается объект Photo."""
        return super().__new__(*args, **kwargs)
