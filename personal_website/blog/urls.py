from blog import views
from django.urls import path

app_name = "blog"

urlpatterns = [
    path("", views.blog, name="blog"),
    path("article/<slug:slug>/", views.ArticleDetailView.as_view(), name="article"),
    path("category/<slug:slug>/", views.category, name="category"),
    path("topic/<slug:slug>/", views.topic, name="topic"),
    path("series/<slug:slug>/", views.series, name="series"),
]
