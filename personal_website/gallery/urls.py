"""Маршруты приложения галереи."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from gallery.views import (
    AlbumDetailView,
    AlbumListView,
    GalleryHomeView,
    PhotoDetailView,
    PhotoListView,
    TagDetailView,
    UploadFormView,
)
from gallery.viewsets import AlbumViewSet, PhotoUploadViewSet, PhotoViewSet, TagViewSet

app_name = "gallery"

# Router для API endpoints
router = DefaultRouter()
router.register(r"albums", AlbumViewSet, basename="album")
router.register(r"photos", PhotoViewSet, basename="photo")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"photos", PhotoUploadViewSet, basename="photo-upload")

# Существующие URL для Django views
urlpatterns = [
    path("", GalleryHomeView.as_view(), name="gallery"),
    path("albums/", AlbumListView.as_view(), name="album-list"),
    path("photos/", PhotoListView.as_view(), name="photo-list"),
    path("upload/", UploadFormView.as_view(), name="upload"),
    path("album/<slug:slug>/", AlbumDetailView.as_view(), name="album-detail"),
    path("photo/<slug:slug>/", PhotoDetailView.as_view(), name="photo-detail"),
    path("tag/<slug:slug>/", TagDetailView.as_view(), name="tag-detail"),
]
