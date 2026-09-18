"""Маршруты приложения страницы Обо мне."""

from django.urls import path
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter

from about.viewsets import AboutPageViewSet

app_name = "about"

# Эндпоинт API: GET /api/about/
router = SimpleRouter()
router.register(r"", AboutPageViewSet, basename="about")

urlpatterns = [
    path("", TemplateView.as_view(template_name="about/about.html"), name="about"),
]
