"""Маршруты приложения галереи."""

from django.urls import path, re_path
from rest_framework.routers import DefaultRouter

from gallery.views import (
    AlbumDetailView,
    AlbumListView,
    EmbedPhotoView,
    GalleryHomeView,
    PhotoDetailView,
    PhotoListView,
    TagDetailView,
    UploadFormView,
)
from gallery.viewsets import AlbumViewSet, PhotoViewSet, TagViewSet, UploadViewSet

app_name = "gallery"

# Router для API endpoints
router = DefaultRouter()
router.register(r"albums", AlbumViewSet, basename="album")
router.register(r"photos", PhotoViewSet, basename="photo")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"", UploadViewSet, basename="upload")

# Существующие URL для Django views
urlpatterns = [
    path("", GalleryHomeView.as_view(), name="gallery"),
    path("albums/", AlbumListView.as_view(), name="album-list"),
    path("photos/", PhotoListView.as_view(), name="photo-list"),
    path("upload/", UploadFormView.as_view(), name="upload"),
    path("album/<int:pk>/", AlbumDetailView.as_view(), name="album-detail"),
    path("photo/<int:pk>/", PhotoDetailView.as_view(), name="photo-detail"),
    re_path(
        r"embed/(?P<pk>[0-9]+)/(?P<size>[0-9]+)\.(?P<ext>[A-Za-z0-9]+)",
        EmbedPhotoView.as_view(),
        name="photo-embed",
    ),
    path("tag/<slug:slug>/", TagDetailView.as_view(), name="tag-detail"),
]
