"""Представления API для Gallery приложения."""

from typing import TYPE_CHECKING, ClassVar

from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from PIL import Image, UnidentifiedImageError
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.pagination import GalleryPhotoPagination
from api.permissions import IsPublicOrAuthor
from gallery.models import Album, Photo, Tag
from gallery.serializers import (
    AlbumDetailSerializer,
    AlbumListSerializer,
    PhotoSerializer,
    TagSerializer,
)

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class AlbumViewSet(viewsets.ReadOnlyModelViewSet):
    """Набор представлений для работы с альбомами."""

    serializer_class = AlbumListSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields: ClassVar[list] = ["tags__slug"]
    search_fields: ClassVar[list] = ["name", "description"]
    ordering_fields: ClassVar[list] = ["created_at", "name", "order"]
    ordering: ClassVar[list] = ["-order", "-created_at"]

    def get_serializer_class(self) -> type:
        """Возвращает сериализатор в зависимости от action."""
        if self.action == "retrieve":
            return AlbumDetailSerializer
        return AlbumListSerializer

    def get_queryset(self) -> "QuerySet[Album]":
        """Возвращать только публичные альбомы в list, все альбомы в retrieve.

        Единая инварианта проекта: списки показывают только public=True,
        детальный просмотр по прямой ссылке доступен для любого объекта
        (share-by-link). Вложенные фотографии альбома в retrieve также
        фильтруются по public=True.
        """
        queryset = Album.objects.select_related("cover").prefetch_related("tags")
        # Для детального просмотра prefetch'им фотографии альбома
        # только публичные (вложенные элементы списка не раскрывают скрытое).
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                Prefetch("photos", queryset=Photo.published.order_by("taken_at")),
            )
        if self.action == "list":
            return queryset.filter(public=True)
        return queryset


class PhotoViewSet(viewsets.ReadOnlyModelViewSet):
    """Набор представлений для работы с фотографиями."""

    serializer_class = PhotoSerializer
    permission_classes: ClassVar[list] = [IsPublicOrAuthor]
    pagination_class = GalleryPhotoPagination
    lookup_field = "pk"
    filter_backends: ClassVar[list] = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields: ClassVar[list] = ["tags__slug"]
    search_fields: ClassVar[list] = ["name", "description", "tags__name"]
    ordering_fields: ClassVar[list] = ["taken_at", "uploaded_at", "name"]
    ordering: ClassVar[list] = ["-taken_at"]

    def get_queryset(self) -> "QuerySet[Photo]":
        """Возвращать только публичные фотографии в list, все фотографии в retrieve.

        Единая инварианта проекта: списки показывают только public=True,
        детальный просмотр по прямой ссылке доступен для любого объекта
        (share-by-link).
        """
        queryset = Photo.objects.select_related("album").prefetch_related("tags")
        if self.action == "list":
            return queryset.filter(public=True)
        return queryset


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
