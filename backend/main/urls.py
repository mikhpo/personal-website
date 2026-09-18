"""Маршруты главного раздела сайта."""

from django.urls import path

from main.views import main, search

app_name = "main"

urlpatterns = [
    path("", main, name="main"),
    path("search/", search, name="search"),
]
