"""Маршруты приложения страницы Обо мне."""

from django.urls import path
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter

from about.viewsets import AboutPageViewSet

app_name = "about"

# Префикс пути /api/about/ задает include в api/urls.py, поэтому в register
# префикс пустой: иначе эндпоинт оказался бы на /api/about/about/.
# SimpleRouter вместо DefaultRouter: корневой view DefaultRouter на пустом
# префиксе перебил бы список содержимого.
router = SimpleRouter()
router.register(r"", AboutPageViewSet, basename="about")

urlpatterns = [
    path("", TemplateView.as_view(template_name="about/about.html"), name="about"),
]
