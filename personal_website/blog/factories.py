"""Фабрики для генерации экземпляров классов с фейковыми данными для тестирования."""
import factory

from blog.models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    """Фабрика для генерации случайных данных для модели Category."""

    class Meta:  # noqa: D106
        model = Category

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    slug = factory.LazyAttribute(lambda _: None)
    image = factory.django.ImageField(color="blue")  # Вы можете настроить цвет или другие параметры
    public = factory.Faker("boolean")

    def __new__(cls, *args, **kwargs) -> "Category":
        """Возвращается объект Category."""
        return super().__new__(*args, **kwargs)
