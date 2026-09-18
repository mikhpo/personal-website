"""Представления главного раздела сайта."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def main(request: HttpRequest) -> HttpResponse:
    """Показ главной страницы сайта.

    Данные загружаются через API в React компонентах.
    """
    return render(request, "main/main.html")


def search(request: HttpRequest) -> HttpResponse:
    """Показ страницы общего поиска по сайту.

    Поисковый запрос передается в React компоненты формы и результатов
    через пропсы, смонтированные шаблоном.
    """
    return render(request, "main/search.html", {"search": request.GET.get("search", "")})
