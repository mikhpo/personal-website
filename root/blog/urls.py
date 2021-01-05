from django.urls import path
from . import views
from .views import ArticleDetailView


app_name = 'blog'  # here for namespacing of urls.

urlpatterns = [
    path("", views.blog, name="blog"),
    path("<slug:slug>/", ArticleDetailView.as_view(), name="article"),
]