"""Маршруты галереи."""

from django.urls import path

from gallery.views import (
    AlbumDetailView,
    AlbumListView,
    GalleryHomeView,
    PhotoDetailView,
    PhotoListView,
    TagDetailView,
    UploadFormView,
)

app_name = "gallery"

urlpatterns = [
    path("", GalleryHomeView.as_view(), name="gallery"),
    path("albums/", AlbumListView.as_view(), name="album-list"),
    path("photos/", PhotoListView.as_view(), name="photo-list"),
    path("photos/<slug:slug>/", PhotoDetailView.as_view(), name="photo-detail"),
    path("albums/<slug:slug>/", AlbumDetailView.as_view(), name="album-detail"),
    path("tags/<slug:slug>/", TagDetailView.as_view(), name="tag-detail"),
    path("upload/", UploadFormView.as_view(), name="upload"),
]
