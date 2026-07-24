"""Представления блога."""

import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.detail import DetailView

from blog.models import Article, Category, Series, Topic

logger = logging.getLogger(__name__)


class ArticleDetailView(DetailView):
    """Представление одной статьи — рендерит React компонент ArticleDetail."""

    model = Article

    def get_context_data(self, **kwargs) -> dict:
        """В контекст добавляется статья и URL для входа."""
        context = super().get_context_data(**kwargs)
        context["login_url"] = f"/accounts/login/?next={self.request.path}"
        return context


def blog(request: HttpRequest) -> HttpResponse:
    """
    Функция, определяющая порядок отображения статей на главной странице блога.
    Отображаются только те статьи, для которых не была установлена невидимость (черновики).
    """
    return render(request, "blog/article_list.html", {})


def category(request: HttpRequest, slug: str) -> HttpResponse:
    """Вывод страницы категории с React компонентом фильтрации."""
    category_obj = get_object_or_404(Category, slug=slug)
    return render(request, "blog/category_detail.html", {"category": category_obj})


def series(request: HttpRequest, slug: str) -> HttpResponse:
    """Вывод страницы серии с React компонентом фильтрации."""
    series_obj = get_object_or_404(Series, slug=slug)
    return render(request, "blog/series_detail.html", {"series": series_obj})


def topic(request: HttpRequest, slug: str) -> HttpResponse:
    """Вывод страницы темы с React компонентом фильтрации."""
    topic_obj = get_object_or_404(Topic, slug=slug)
    return render(request, "blog/topic_detail.html", {"topic": topic_obj})
