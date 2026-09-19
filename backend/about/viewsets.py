"""Представления API приложения страницы Обо мне."""

from typing import ClassVar

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from about.models import About
from about.serializers import AboutSerializer


class AboutViewSet(viewsets.ViewSet):
    """Представление страницы Обо мне для API.

    Страница единственная, поэтому единственное действие - чтение
    содержимого записи-синглтона без детализации.
    """

    permission_classes: ClassVar[list] = [AllowAny]

    def list(self, request: Request) -> Response:  # noqa: ARG002
        """Возвращает содержимое страницы Обо мне."""
        about_page = About.get_solo()
        serializer = AboutSerializer(about_page)
        return Response(serializer.data)
