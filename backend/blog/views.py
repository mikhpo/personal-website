"""Представления блога."""

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from blog.mixins import StaffRequiredMixin
from blog.models import Article, Category, Series, Topic

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

logger = logging.getLogger(settings.PROJECT_NAME)


class ArticleDetailView(DetailView):
    """Представление одной статьи - рендерит React компонент ArticleDetail."""

    model = Article

    def get_queryset(self) -> "QuerySet[Article]":
        """Возвращает все статьи.

        Фильтрация по public выполняется в списке (см. ArticleViewSet);
        детальный просмотр доступен всем.
        """
        return Article.objects.all()

    def get_context_data(self, **kwargs) -> dict:
        """В контекст добавляется статья и URL для входа."""
        context = super().get_context_data(**kwargs)
        context["login_url"] = f"/accounts/login/?next={self.request.path}"
        return context


class ArticleCreateView(StaffRequiredMixin, TemplateView):
    """Страница создания статьи - рендерит React компонент ArticleForm."""

    template_name = "blog/article_form.html"


class ArticleEditView(StaffRequiredMixin, DetailView):
    """Страница редактирования статьи - рендерит React компонент ArticleForm."""

    model = Article
    context_object_name = "article"
    template_name = "blog/article_form.html"


def blog(request: HttpRequest) -> HttpResponse:
    """
    Функция, определяющая порядок отображения статей на главной странице блога.
    Отображаются только те статьи, для которых не была установлена невидимость (черновики).
    Поисковый запрос из GET-параметров передается в React компоненты страницы.
    """
    return render(request, "blog/article_list.html", {"search": request.GET.get("search", "")})


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
