"""Маршруты главного раздела сайта."""
from django.urls import path

from main.views import main

app_name = "main"

urlpatterns = [
    path("", main, name="main"),
]
