"""Представления главного раздела сайта."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def main(request: HttpRequest) -> HttpResponse:
    """Показ главной страницы сайта.

    Данные загружаются через API в React компонентах.
    """
    return render(request, "main/main.html")
