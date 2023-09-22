from django.urls import path
from gallery import views

app_name = "gallery"

urlpatterns = [
    path("", views.GalleryHomeView.as_view(), name="gallery"),
    path("albums/", views.AlbumListView.as_view(), name="album-list"),
    path("photos/", views.PhotoListView.as_view(), name="photo-list"),
    path("tags/", views.TagListView.as_view(), name="tag-list"),
    path("photos/<slug:slug>/", views.PhotoDetailView.as_view(), name="photo-detail"),
    path("albums/<slug:slug>/", views.AlbumDetailView.as_view(), name="album-detail"),
    path("tags/<slug:slug>/", views.TagDetailView.as_view(), name="tag-detail"),
]
