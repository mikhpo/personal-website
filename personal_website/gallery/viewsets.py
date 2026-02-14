"""Представления API для Gallery приложения."""

from typing import TYPE_CHECKING, ClassVar

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.permissions import IsPublicOrAuthor
from gallery.models import Album, Photo, Tag
from gallery.serializers import AlbumSerializer, PhotoSerializer, TagSerializer

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class AlbumViewSet(viewsets.ReadOnlyModelViewSet):
    """Набор представлений для работы с альбомами."""

    serializer_class = AlbumSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "slug"
    filter_backends: ClassVar[list] = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields: ClassVar[list] = ["tags__slug"]
    search_fields: ClassVar[list] = ["name", "description"]
    ordering_fields: ClassVar[list] = ["created_at", "name", "order"]
    ordering: ClassVar[list] = ["order", "-created_at"]

    def get_queryset(self) -> "QuerySet[Album]":
        """Возвращать все альбомы для staff пользователей, только публичные для остальных."""
        queryset = Album.objects.select_related("cover").prefetch_related("tags")
        if hasattr(self.request.user, "is_staff") and self.request.user.is_staff:
            return queryset
        return queryset.filter(public=True)


class PhotoViewSet(viewsets.ReadOnlyModelViewSet):
    """Набор представлений для работы с фотографиями."""

    serializer_class = PhotoSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "slug"
    filter_backends: ClassVar[list] = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields: ClassVar[list] = ["album__slug", "tags__slug", "album"]
    search_fields: ClassVar[list] = ["name", "description", "tags__name"]
    ordering_fields: ClassVar[list] = ["uploaded_at", "name"]
    ordering: ClassVar[list] = ["-uploaded_at"]

    def get_queryset(self) -> "QuerySet[Photo]":
        """Возвращать все фотографии для staff пользователей, только публичные для остальных."""
        queryset = Photo.objects.select_related("album").prefetch_related("tags")
        if hasattr(self.request.user, "is_staff") and self.request.user.is_staff:
            return queryset
        return queryset.filter(public=True)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Набор представлений для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes: ClassVar[list] = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"
    filter_backends: ClassVar[list] = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar[list] = ["name"]
    ordering_fields: ClassVar[list] = ["name"]
    ordering: ClassVar[list] = ["name"]
