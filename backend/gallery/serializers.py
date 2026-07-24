"""Сериализаторы для Gallery API."""

from rest_framework import serializers

from gallery.models import Album, Photo, Tag


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тега."""

    class Meta:
        """Мета-информация о сериализаторе тега."""

        model = Tag
        fields = "__all__"


class PhotoSerializer(serializers.ModelSerializer):
    """Сериализатор для модели фотографии."""

    tags = TagSerializer(many=True, read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    camera = serializers.SerializerMethodField()
    lens_model = serializers.SerializerMethodField()
    aperture = serializers.SerializerMethodField()
    exposure = serializers.SerializerMethodField()
    iso = serializers.SerializerMethodField()
    focal_length = serializers.SerializerMethodField()

    class Meta:
        """Мета-информация о сериализаторе фотографии."""

        model = Photo
        fields = "__all__"

    def get_thumbnail_url(self, obj: Photo) -> str:
        """Получить URL миниатюры."""
        return obj.image_thumbnail.url if obj.image_thumbnail else ""

    def get_preview_url(self, obj: Photo) -> str:
        """Получить URL превью."""
        return obj.image_preview.url if obj.image_preview else ""

    def get_image_url(self, obj: Photo) -> str:
        """Получить URL оригинального изображения."""
        return obj.image.url if obj.image else ""

    def get_camera(self, obj: Photo) -> str:
        """Получить название камеры."""
        return obj.camera or ""

    def get_lens_model(self, obj: Photo) -> str:
        """Получить модель объектива."""
        return obj.lens_model or ""

    def get_aperture(self, obj: Photo) -> str | None:
        """Получить диафрагму."""
        return obj.aperture

    def get_exposure(self, obj: Photo) -> str | None:
        """Получить выдержку."""
        return obj.exposure

    def get_iso(self, obj: Photo) -> int | None:
        """Получить ISO."""
        return obj.iso

    def get_focal_length(self, obj: Photo) -> int | None:
        """Получить фокусное расстояние."""
        return obj.focal_length


class AlbumListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка альбомов (без фотографий)."""

    tags = TagSerializer(many=True, read_only=True)
    cover_thumbnail_url = serializers.SerializerMethodField()
    photos_count = serializers.IntegerField(source="photos.count", read_only=True)

    class Meta:
        """Мета-информация о сериализаторе альбома."""

        model = Album
        fields = "__all__"

    def get_cover_thumbnail_url(self, obj: Album) -> str:
        """Получить URL миниатюры обложки альбома."""
        if obj.cover and obj.cover.image_thumbnail:
            return obj.cover.image_thumbnail.url
        return ""


class AlbumDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра альбома (с фотографиями)."""

    tags = TagSerializer(many=True, read_only=True)
    cover_thumbnail_url = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        """Мета-информация о сериализаторе альбома."""

        model = Album
        fields = "__all__"

    def get_cover_thumbnail_url(self, obj: Album) -> str:
        """Получить URL миниатюры обложки альбома."""
        if obj.cover and obj.cover.image_thumbnail:
            return obj.cover.image_thumbnail.url
        return ""
