"""Представления блога."""
import logging
from typing import Any

from django.conf import settings
from django.core.paginator import Page, Paginator
from django.db.models.manager import BaseManager
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic.detail import DetailView

from blog.forms import NewCommentForm
from blog.models import Article, Category, Comment, Series, Topic

logger = logging.getLogger(settings.PROJECT_NAME)


class ArticleDetailView(DetailView):
    """
    Представление одной статьи, в котором отображается статья,
    детали (дата создания, дата редактирования) и комментарии.
    """

    model = Article

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """В контекст ответа добавляются комментарии к статье и форма создания комментария."""
        data = super().get_context_data(**kwargs)

        # Добавляются комментарии к статье, отсортированные в порядке от старых к новым.
        comments_connected = Comment.objects.filter(article=self.get_object())
        data["comments"] = comments_connected

        # Если пользователь авторизован, то появляется форма добавления комментария.
        if self.request.user.is_authenticated:
            data["comment_form"] = NewCommentForm(instance=self.request.user)

        return data

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Функция для добавления комментариев к статьям."""
        new_comment = Comment(
            content=request.POST.get("content"),
            author=self.request.user,
            article=self.get_object(),
        )
        new_comment.save()
        user = self.request.user
        article = self.get_object()
        logger.info(f"Пользователь {user} оставил комментарий к статье {article}")
        return self.get(self, request, *args, **kwargs)


def paginate(request: HttpRequest, objects: BaseManager) -> Page:
    """Фукнция для разбивки отображения списка объектов по страницам."""
    paginator = Paginator(objects, 5)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def blog(request: HttpRequest) -> HttpResponse:
    """
    Функция, определяющая порядок отображения статей на главной странице блога.
    Добавлена разбивка по страницам. Здесь указано количество статей на страницу.
    Отображаются только те статьи, для которых не была установлена невидимость (черновики).
    """
    content = Article.published.all()
    return render(request, "blog/article_list.html", {"page_obj": paginate(request, content)})


def category(request: HttpRequest, slug: str) -> HttpResponse:
    """Вывод всех статей, соответствующих определенной категории."""
    category = Category.objects.get(slug=slug)
    articles = category.article_set.filter(public=True)
    return render(request, "blog/article_list.html", {"page_obj": paginate(request, articles)})


def series(request: HttpRequest, slug: str) -> HttpResponse:
    """Вывод всех статей, соответствующих определенной серии."""
    series = Series.objects.get(slug=slug)
    articles = series.article_set.filter(public=True)
    return render(request, "blog/article_list.html", {"page_obj": paginate(request, articles)})


def topic(request: HttpRequest, slug: str) -> HttpResponse:
    """Вывод всех статей, соответствующих определенной теме."""
    topic = Topic.objects.get(slug=slug)
    articles = topic.article_set.filter(public=True)
    return render(request, "blog/article_list.html", {"page_obj": paginate(request, articles)})
