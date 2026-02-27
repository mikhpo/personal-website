"""Представления API для Gallery приложения."""

from typing import TYPE_CHECKING, ClassVar

from django_filters.rest_framework import DjangoFilterBackend
from PIL import Image, UnidentifiedImageError
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.permissions import IsPublicOrAuthor
from gallery.models import Album, Photo, Tag
from gallery.serializers import AlbumSerializer, PhotoSerializer, TagSerializer

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class AlbumViewSet(viewsets.ReadOnlyModelViewSet):
    """Набор представлений для работы с альбомами."""

    serializer_class = AlbumSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields: ClassVar[list] = ["tags__slug"]
    search_fields: ClassVar[list] = ["name", "description"]
    ordering_fields: ClassVar[list] = ["created_at", "name", "order"]
    ordering: ClassVar[list] = ["order", "-created_at"]

    def get_queryset(self) -> "QuerySet[Album]":
        """Возвращать все альбомы для staff пользователей, только публичные для остальных."""
        queryset = Album.objects.select_related("cover").prefetch_related("tags", "photos")
        if hasattr(self.request.user, "is_staff") and self.request.user.is_staff:
            return queryset
        return queryset.filter(public=True)


class PhotoViewSet(viewsets.ReadOnlyModelViewSet):
    """Набор представлений для работы с фотографиями."""

    serializer_class = PhotoSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields: ClassVar[list] = ["tags__slug"]
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
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar[list] = ["name"]
    ordering_fields: ClassVar[list] = ["name"]
    ordering: ClassVar[list] = ["name"]


class UploadViewSet(viewsets.ViewSet):
    """Набор представлений для загрузки фотографий."""

    permission_classes: ClassVar[list] = [IsAdminUser]

    @action(detail=False, methods=["post"])
    def upload(self, request):  # noqa: ANN001, ANN201
        """Загрузить одну или несколько фотографий в альбом."""
        album_id = request.data.get("album_id")
        files = request.FILES.getlist("photos")

        if not album_id:
            return Response(
                {"error": "Album ID required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            album = Album.objects.get(id=album_id)
        except Album.DoesNotExist:
            return Response(
                {"error": "Album not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        results = []
        for file in files:
            try:
                # Валидация изображения
                image = Image.open(file)
                image.verify()

                # Создание фотографии
                photo = Photo.objects.create(image=file, album=album)
                results.append(
                    {
                        "success": True,
                        "filename": file.name,
                        "id": photo.id,
                    },
                )
            except UnidentifiedImageError:  # noqa: PERF203
                results.append(
                    {
                        "success": False,
                        "filename": file.name,
                        "error": "Not an image",
                    },
                )
            except Exception as e:  # noqa: BLE001
                results.append(
                    {
                        "success": False,
                        "filename": file.name,
                        "error": str(e),
                    },
                )

        return Response({"results": results}, status=status.HTTP_201_CREATED)
