"""Представления API приложения страницы Обо мне."""

from typing import ClassVar

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from about.models import AboutPage
from about.serializers import AboutPageSerializer


class AboutPageViewSet(viewsets.ViewSet):
    """Представление страницы Обо мне для API.

    Страница единственная, поэтому единственное действие - чтение
    содержимого записи-синглтона без детализации.
    """

    permission_classes: ClassVar[list] = [AllowAny]

    def list(self, request: Request) -> Response:  # noqa: ARG002
        """Возвращает содержимое страницы Обо мне."""
        about_page = AboutPage.get_solo()
        serializer = AboutPageSerializer(about_page)
        return Response(serializer.data)
