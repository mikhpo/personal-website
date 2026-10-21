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
    """Сериализатор для модели фотографии.

    Поля соседей по альбому здесь отсутствуют: списочные данные их не
    используют, детальному просмотру их добавляет PhotoDetailSerializer.
    """

    tags = TagSerializer(many=True, read_only=True)
    album_name = serializers.CharField(source="album.name", read_only=True)
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


class PhotoDetailSerializer(PhotoSerializer):
    """Сериализатор детального просмотра фотографии с соседями по альбому.

    Соседи вычисляются один раз на объект и хранятся по его ключу: списковая
    выдача с many=True не смешает соседей разных фотографий.
    """

    previous_id = serializers.SerializerMethodField()
    next_id = serializers.SerializerMethodField()

    def _get_neighbors(self, obj: Photo) -> tuple[int | None, int | None]:
        """Получить соседей фотографии, кэшируя выборку по ключу объекта."""
        cache = self.__dict__.setdefault("_neighbors", {})
        if obj.pk not in cache:
            cache[obj.pk] = obj.get_neighbor_ids()
        return cache[obj.pk]

    def get_previous_id(self, obj: Photo) -> int | None:
        """Получить id предыдущей публичной фотографии альбома."""
        return self._get_neighbors(obj)[0]

    def get_next_id(self, obj: Photo) -> int | None:
        """Получить id следующей публичной фотографии альбома."""
        return self._get_neighbors(obj)[1]


class AlbumBaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для альбома с общими полями."""

    tags = TagSerializer(many=True, read_only=True)
    cover_thumbnail_url = serializers.SerializerMethodField()

    def get_cover_thumbnail_url(self, obj: Album) -> str:
        """Получить URL миниатюры обложки альбома."""
        if obj.cover and obj.cover.image_thumbnail:
            return obj.cover.image_thumbnail.url
        return ""

    class Meta:
        """Мета-информация о сериализаторе альбома."""

        model = Album
        abstract = True


class AlbumListSerializer(AlbumBaseSerializer):
    """Сериализатор для списка альбомов (без фотографий)."""

    photos_count = serializers.IntegerField(source="photos.count", read_only=True)

    class Meta(AlbumBaseSerializer.Meta):
        """Мета-информация о сериализаторе альбома."""

        fields = "__all__"


class AlbumDetailSerializer(AlbumBaseSerializer):
    """Сериализатор для детального просмотра альбома (с фотографиями)."""

    photos = PhotoSerializer(many=True, read_only=True)

    class Meta(AlbumBaseSerializer.Meta):
        """Мета-информация о сериализаторе альбома."""

        fields = "__all__"
