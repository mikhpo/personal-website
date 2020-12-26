from django.urls import path
from . import views


app_name = 'blog'  # here for namespacing of urls.

urlpatterns = [
    path("", views.blogpage, name="blogpage"),
]