"""Маршруты главного раздела сайта."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from main.views import main, search
from main.viewsets import AboutPageViewSet

app_name = "main"

# Router для API endpoints
router = DefaultRouter()
router.register(r"about", AboutPageViewSet, basename="about")

urlpatterns = [
    path("", main, name="main"),
    path("search/", search, name="search"),
]
