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


class AlbumSerializer(serializers.ModelSerializer):
    """Сериализатор для модели альбома."""

    tags = TagSerializer(many=True, read_only=True)
    cover_thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        """Мета-информация о сериализаторе альбома."""

        model = Album
        fields = "__all__"

    def get_cover_thumbnail_url(self, obj: Album) -> str:
        """Получить URL миниатюры обложки альбома."""
        if obj.cover and obj.cover.image_thumbnail:
            return obj.cover.image_thumbnail.url
        return ""
