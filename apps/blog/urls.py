from django.urls import path
from . import views
from .views import ArticleDetailView

app_name = 'blog' 

urlpatterns = [
    path("", views.blog, name="blog"),
    path("category/<slug:slug>/", views.category, name="category"),
    path("topic/<slug:slug>/", views.topic, name="topic"),
    path("series/<slug:slug>/", views.series, name="series"),
    path("article/<slug:slug>/", ArticleDetailView.as_view(), name="article"),
    path("<slug:slug>/", ArticleDetailView.as_view(), name="article_shortcut"),
]