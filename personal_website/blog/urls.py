"""Маршруты блога."""
from django.urls import path

from blog.views import ArticleDetailView, blog, category, series, topic

app_name = "blog"

urlpatterns = [
    path("", blog, name="blog"),
    path("article/<slug:slug>/", ArticleDetailView.as_view(), name="article"),
    path("category/<slug:slug>/", category, name="category"),
    path("topic/<slug:slug>/", topic, name="topic"),
    path("series/<slug:slug>/", series, name="series"),
]
