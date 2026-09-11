"""Сериализаторы для Blog API."""

from typing import ClassVar

from rest_framework import serializers

from blog.models import Article, Category, Comment, Series, Topic


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели категории."""

    class Meta:
        """Мета-информация о сериализаторе категории."""

        model = Category
        fields = "__all__"


class TopicSerializer(serializers.ModelSerializer):
    """Сериализатор для модели темы."""

    class Meta:
        """Мета-информация о сериализаторе темы."""

        model = Topic
        fields = "__all__"


class SeriesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели серии."""

    class Meta:
        """Мета-информация о сериализаторе серии."""

        model = Series
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""

    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        """Мета-информация о сериализаторе комментария."""

        model = Comment
        fields: ClassVar[list[str]] = ["id", "article", "author", "author_username", "content", "posted"]
        read_only_fields: ClassVar[list[str]] = ["author", "author_username", "posted"]


class ArticleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели статьи."""

    author_username = serializers.CharField(source="author.username", read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    topics = TopicSerializer(many=True, read_only=True)
    series = SeriesSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    url = serializers.SerializerMethodField()

    def get_url(self, obj: Article) -> str:
        """Возвращает абсолютный URL статьи."""
        return obj.get_absolute_url()

    class Meta:
        """Мета-информация о сериализаторе статьи."""

        model = Article
        fields = "__all__"


class ClearableManyRelatedField(serializers.ManyRelatedField):
    """Список первичных ключей M2M, допускающий очистку связей в multipart-запросе.

    В FormData невозможно передать пустой список, поэтому клиент отправляет
    ключ с пустым значением, и такое значение трактуется как "убрать все связи".
    """

    def get_value(self, dictionary):  # noqa: ANN001, ANN201
        """В multipart-запросе пустая строка доходит до to_internal_value как маркер."""
        if serializers.html.is_html_input(dictionary):
            if self.field_name not in dictionary:
                if getattr(self.root, "partial", False):
                    return serializers.empty
                return []
            return dictionary.getlist(self.field_name)
        return super().get_value(dictionary)

    def to_internal_value(self, data):  # noqa: ANN001, ANN201
        """Пустая строка и пустой список означают очистку связей."""
        if data in ("", [""], []):
            return []
        return super().to_internal_value(data)


def _clearable_pk_field(queryset) -> ClearableManyRelatedField:  # noqa: ANN001
    """Создает поле списка первичных ключей M2M с поддержкой очистки."""
    return ClearableManyRelatedField(
        child_relation=serializers.PrimaryKeyRelatedField(queryset=queryset),
        required=False,
    )


class ArticleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор записи статьи (создание и обновление через форму редактора).

    Автор, слаг и даты заполняются на сервере, поэтому в сериализатор
    не включены. Категории, темы и серии передаются списками первичных
    ключей; пустое значение ключа означает очистку связей. Ответ отдается
    в полном представлении ArticleSerializer, чтобы клиент получал url
    и вложенные объекты статьи.
    """

    categories = _clearable_pk_field(Category.objects.all())
    topics = _clearable_pk_field(Topic.objects.all())
    series = _clearable_pk_field(Series.objects.all())
    remove_image = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        """Мета-информация о сериализаторе записи статьи."""

        model = Article
        fields: ClassVar[list[str]] = [
            "title",
            "description",
            "content",
            "public",
            "image",
            "remove_image",
            "categories",
            "topics",
            "series",
        ]

    def create(self, validated_data: dict) -> Article:
        """Создать статью без служебного флага очистки обложки."""
        validated_data.pop("remove_image", None)
        return super().create(validated_data)

    def update(self, instance: Article, validated_data: dict) -> Article:
        """Очистить обложку по флагу remove_image (файл удалит django-cleanup)."""
        if validated_data.pop("remove_image", False) and "image" not in validated_data:
            instance.image = ""
        return super().update(instance, validated_data)

    def to_representation(self, instance: Article) -> dict:
        """Отдавать ответ статьи в полном представлении (url, вложенные объекты)."""
        return ArticleSerializer(instance, context=self.context).data
