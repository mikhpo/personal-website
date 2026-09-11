"""Представления API для Blog приложения."""

from typing import TYPE_CHECKING, ClassVar

from auditlog.context import set_actor
from django.contrib.auth.base_user import AbstractBaseUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.filters import DatabaseSearchFilter
from api.mixins import AuditlogActorMixin
from api.permissions import IsAuthorOrReadOnly, IsPublicOrAuthor
from blog.models import Article, Category, Comment, Series, Topic
from blog.serializers import (
    ArticleSerializer,
    ArticleWriteSerializer,
    CategorySerializer,
    CommentSerializer,
    SeriesSerializer,
    TopicSerializer,
)

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class CategoryViewSet(AuditlogActorMixin, viewsets.ModelViewSet):
    """Набор представлений для работы с категориями (полный CRUD)."""

    serializer_class = CategorySerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar[list] = ["name", "description"]
    ordering_fields: ClassVar[list] = ["name"]
    ordering: ClassVar[list] = ["name"]

    def get_queryset(self) -> "QuerySet[Category]":
        """В list отдаёт публичные категории, а администратору - все.

        Полный справочник нужен staff в форме статьи: привязанные
        к статье непубличные категории не должны пропадать из селектора.
        """
        queryset = Category.objects.all()
        if self.action == "list":
            user = self.request.user
            if isinstance(user, AbstractBaseUser) and user.is_staff:
                return queryset
            return queryset.filter(public=True)
        return queryset


class TopicViewSet(AuditlogActorMixin, viewsets.ModelViewSet):
    """Набор представлений для работы с темами (полный CRUD)."""

    serializer_class = TopicSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar[list] = ["name", "description"]
    ordering_fields: ClassVar[list] = ["name"]
    ordering: ClassVar[list] = ["name"]

    def get_queryset(self) -> "QuerySet[Topic]":
        """В list отдаёт публичные темы, а администратору - все."""
        queryset = Topic.objects.all()
        if self.action == "list":
            user = self.request.user
            if isinstance(user, AbstractBaseUser) and user.is_staff:
                return queryset
            return queryset.filter(public=True)
        return queryset


class SeriesViewSet(AuditlogActorMixin, viewsets.ModelViewSet):
    """Набор представлений для работы с сериями (полный CRUD)."""

    serializer_class = SeriesSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar[list] = ["name", "description"]
    ordering_fields: ClassVar[list] = ["name"]
    ordering: ClassVar[list] = ["name"]

    def get_queryset(self) -> "QuerySet[Series]":
        """В list отдаёт публичные серии, а администратору - все."""
        queryset = Series.objects.all()
        if self.action == "list":
            user = self.request.user
            if isinstance(user, AbstractBaseUser) and user.is_staff:
                return queryset
            return queryset.filter(public=True)
        return queryset


class ArticleViewSet(AuditlogActorMixin, viewsets.ModelViewSet):
    """Набор представлений для работы со статьями (полный CRUD)."""

    serializer_class = ArticleSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "pk"
    # DatabaseSearchFilter после OrderingFilter: сортировка по релевантности
    # (-rank) не должна перезаписываться дефолтным ordering вьюхи.
    filter_backends: ClassVar[list] = [DjangoFilterBackend, filters.OrderingFilter, DatabaseSearchFilter]
    filterset_fields: ClassVar[list] = ["categories__slug", "topics__slug", "series__slug"]
    search_fields: ClassVar[list] = ["title", "description", "content"]
    ordering_fields: ClassVar[list] = ["published_at", "modified_at", "title"]
    ordering: ClassVar[list] = ["-published_at"]

    def get_serializer_class(self) -> type:
        """Для записи - сериализатор с первичными ключами M2M, для чтения - полный."""
        if self.action in {"create", "update", "partial_update"}:
            return ArticleWriteSerializer
        return ArticleSerializer

    def get_queryset(self) -> "QuerySet[Article]":
        """В list отдаёт публичные статьи, а администраторам - все, включая черновики.

        select_related/prefetch_related оптимизируют сериализацию вложенных
        объектов (автор, категории, темы, серии, комментарии). Черновики нужны
        staff в списке, чтобы находить неопубликованные статьи для редактирования.
        """
        queryset = Article.objects.select_related("author").prefetch_related(
            "categories",
            "topics",
            "series",
            "comments__author",
        )
        if self.action == "list":
            user = self.request.user
            if isinstance(user, AbstractBaseUser) and user.is_staff:
                return queryset
            return queryset.filter(public=True)
        return queryset

    def perform_create(self, serializer) -> None:  # noqa: ANN001
        """Проставить автора статьи из текущего пользователя и зафиксировать его в аудите."""
        with set_actor(self.request.user, remote_addr=self.request.META.get("HTTP_X_REAL_IP")):
            serializer.save(author=self.request.user)


class CommentViewSet(AuditlogActorMixin, viewsets.ModelViewSet):
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
        """Автоматически устанавливает автора комментария и фиксирует его в аудите."""
        with set_actor(self.request.user, remote_addr=self.request.META.get("HTTP_X_REAL_IP")):
            serializer.save(author=self.request.user)
