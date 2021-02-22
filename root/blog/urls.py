from django.urls import path
from . import views
from .views import ArticleDetailView

app_name = 'blog' 

urlpatterns = [
    path("", views.blog, name="blog"),
    path("<slug:slug>/", ArticleDetailView.as_view(), name="article"),
    path("<int:pk>/", ArticleDetailView.as_view(), name="article"),
]