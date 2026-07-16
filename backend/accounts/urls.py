"""Маршруты системы авторизации пользователей."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from accounts.views import signup
from accounts.viewsets import UserViewSet

app_name = "accounts"

router = DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("signup/", signup, name="signup"),
]
