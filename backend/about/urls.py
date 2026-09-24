"""Маршруты приложения Обо мне."""

from django.urls import path
from rest_framework.routers import SimpleRouter

from about.views import AboutView
from about.viewsets import AboutViewSet

app_name = "about"

# Эндпоинт API: GET /api/about/
router = SimpleRouter()
router.register(r"", AboutViewSet, basename="about")

urlpatterns = [
    path("", AboutView.as_view(), name="about"),
]
