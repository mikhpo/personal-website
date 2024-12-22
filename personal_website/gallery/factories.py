"""Фабрики для генерации объектов галереи со случайными данными."""

import factory
from django.utils.timezone import now
from faker import Faker

from gallery.models import Album, Photo, Tag
from gallery.schemas import ExifData

fake = Faker()


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


class ExifDataFactory(factory.Factory):
    """Фабрика данных EXIF."""

    class Meta:  # noqa: D106
        model = ExifData

    make = factory.Faker("random_element", elements=("Canon", "Nikon"))
    model = factory.Faker(
        "random_element",
        elements=(
            "EOS 5D Mark II",
            "EOS 5D Mark III",
            "EOS 5D Mark IV",
            "EOS 5DS",
            "EOS 6D",
            "EOS 6D Mark II",
            "D800",
            "D810",
            "D850",
            "D700",
            "D750",
            "D780",
        ),
    )
    lens_model = factory.Faker(
        "random_element",
        elements=(
            "EF 50mm f/1.4 USM",
            "EF 24-105mm f/4L IS USM",
            "EF 17-40mm f/4L USM",
            "EF 70-200mm f/4L IS USM",
            "AF-S 14-24 mm f/2.8G ED N",
            "AF-S 24-70 mm f/2.8G ED N",
            "AF-S 70-200 mm f/2.8G ED VR II",
        ),
    )
    f_number = factory.Faker("pyfloat", right_digits=1, positive=True, min_value=1, max_value=22)
    iso_speed = factory.Faker("pyint", min_value=40, max_value=3200, step=100)
    focal_length = factory.Faker("pyint", min_value=14, max_value=200)

    @factory.lazy_attribute
    def exposure_time(self) -> None:  # noqa: D102
        greater_than_second = fake.pybool()
        if greater_than_second:
            return fake.pyint(min_value=60, max_value=1800, step=60)
        denominator = fake.pyint(min_value=10, max_value=400, step=10)
        return 1 / denominator

    def __new__(cls, *args, **kwargs) -> "Meta.model":
        """Фабрика данных EXIF."""
        return super().__new__(*args, **kwargs)
