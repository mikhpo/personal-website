"""Представления API для Blog приложения."""

from typing import TYPE_CHECKING, ClassVar

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.permissions import IsAuthorOrReadOnly, IsPublicOrAuthor
from blog.models import Article, Category, Comment, Series, Topic
from blog.serializers import (
    ArticleSerializer,
    CategorySerializer,
    CommentSerializer,
    SeriesSerializer,
    TopicSerializer,
)

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class CategoryViewSet(viewsets.ModelViewSet):
    """Набор представлений для работы с категориями (полный CRUD)."""

    serializer_class = CategorySerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar[list] = ["name", "description"]
    ordering_fields: ClassVar[list] = ["name"]
    ordering: ClassVar[list] = ["name"]

    def get_queryset(self) -> "QuerySet[Category]":
        """Возвращать все категории для staff пользователей, только публичные для остальных."""
        queryset = Category.objects.all()
        if hasattr(self.request.user, "is_staff") and self.request.user.is_staff:
            return queryset
        return queryset.filter(public=True)


class TopicViewSet(viewsets.ModelViewSet):
    """Набор представлений для работы с темами (полный CRUD)."""

    serializer_class = TopicSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar[list] = ["name", "description"]
    ordering_fields: ClassVar[list] = ["name"]
    ordering: ClassVar[list] = ["name"]

    def get_queryset(self) -> "QuerySet[Topic]":
        """Возвращать все темы для staff пользователей, только публичные для остальных."""
        queryset = Topic.objects.all()
        if hasattr(self.request.user, "is_staff") and self.request.user.is_staff:
            return queryset
        return queryset.filter(public=True)


class SeriesViewSet(viewsets.ModelViewSet):
    """Набор представлений для работы с сериями (полный CRUD)."""

    serializer_class = SeriesSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar[list] = ["name", "description"]
    ordering_fields: ClassVar[list] = ["name"]
    ordering: ClassVar[list] = ["name"]

    def get_queryset(self) -> "QuerySet[Series]":
        """Возвращать все серии для staff пользователей, только публичные для остальных."""
        queryset = Series.objects.all()
        if hasattr(self.request.user, "is_staff") and self.request.user.is_staff:
            return queryset
        return queryset.filter(public=True)


class ArticleViewSet(viewsets.ModelViewSet):
    """Набор представлений для работы со статьями (полный CRUD)."""

    serializer_class = ArticleSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields: ClassVar[list] = ["categories__slug", "topics__slug", "series__slug"]
    search_fields: ClassVar[list] = ["title", "description", "content"]
    ordering_fields: ClassVar[list] = ["published_at", "modified_at", "title"]
    ordering: ClassVar[list] = ["-published_at"]

    def get_queryset(self) -> "QuerySet[Article]":
        """Возвращать все статьи для staff пользователей, только публичные для остальных.

        Использует select_related и prefetch_related для оптимизации запросов к базе данных
        и предотвращения множественных запросов при сериализации вложенных объектов.
        """
        queryset = Article.objects.select_related("author").prefetch_related(
            "categories",
            "topics",
            "series",
            "comments__author",
        )
        if hasattr(self.request.user, "is_staff") and self.request.user.is_staff:
            return queryset
        return queryset.filter(public=True)


class CommentViewSet(viewsets.ModelViewSet):
    """Набор представлений для работы с комментариями (полный CRUD)."""

    serializer_class = CommentSerializer
    permission_classes: ClassVar[list] = [IsAuthenticatedOrReadOnly]
    filter_backends: ClassVar[list] = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields: ClassVar[list] = ["article__slug", "author__username", "article"]
    ordering: ClassVar[list] = ["posted"]

    def get_queryset(self) -> "QuerySet[Comment]":
        """Возвращать все комментарии с оптимизированными запросами к базе данных."""
        return Comment.objects.select_related("author", "article")

    def get_permissions(self) -> list:
        """Возвращает список прав доступа для текущего действия.

        Для update, partial_update и delete требуется авторство комментария.
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), IsAuthorOrReadOnly()]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer) -> None:  # noqa: ANN001
        """Автоматически устанавливает автора комментария."""
        serializer.save(author=self.request.user)
