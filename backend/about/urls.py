"""Маршруты приложения страницы Обо мне."""

from django.urls import path
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter

from about.viewsets import AboutPageViewSet

app_name = "about"

# Router для API endpoint: префикс пустой, эндпоинт /api/about/ монтируется
# в api/urls.py путем включения с префиксом about/
router = SimpleRouter()
router.register(r"", AboutPageViewSet, basename="about")

urlpatterns = [
    path("", TemplateView.as_view(template_name="about/about.html"), name="about"),
]
