"""Маршруты блога."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from blog.views import ArticleDetailView, blog, category, series, topic
from blog.viewsets import ArticleViewSet, CategoryViewSet, CommentViewSet, SeriesViewSet, TopicViewSet

app_name = "blog"

# Router для API endpoints
router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"topics", TopicViewSet, basename="topic")
router.register(r"series", SeriesViewSet, basename="series")
router.register(r"articles", ArticleViewSet, basename="article")
router.register(r"comments", CommentViewSet, basename="comment")

# Существующие URL для Django views
urlpatterns = [
    path("", blog, name="blog"),
    path("article/<slug:slug>/", ArticleDetailView.as_view(), name="article"),
    path("category/<slug:slug>/", category, name="category"),
    path("topic/<slug:slug>/", topic, name="topic"),
    path("series/<slug:slug>/", series, name="series"),
]
