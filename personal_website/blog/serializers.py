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
