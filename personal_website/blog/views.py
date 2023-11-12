import logging

from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic.detail import DetailView

from .forms import NewCommentForm
from .models import Article, Category, Comment, Series, Topic

logger = logging.getLogger(settings.PROJECT_NAME)


class ArticleDetailView(DetailView):
    """
    Представление одной статьи, в котором отображается статья,
    детали (дата создания, дата редактирования) и комментарии.
    """

    model = Article

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        # Добавляются комментарии к статье, отсортированные в порядке от старых к новым.
        comments_connected = Comment.objects.filter(article=self.get_object())
        data["comments"] = comments_connected

        # Если пользователь авторизован, то появляется форма добавления комментария.
        if self.request.user.is_authenticated:
            data["comment_form"] = NewCommentForm(instance=self.request.user)

        return data

    def post(self, request, *args, **kwargs):
        """
        Функция для добавления комментариев к статьям.
        """
        new_comment = Comment(
            content=request.POST.get("content"),
            author=self.request.user,
            article=self.get_object(),
        )
        new_comment.save()
        logger.info(
            f'Пользователь {self.request.user} оставил комментарий к статье "{self.get_object()}"'
        )
        return self.get(self, request, *args, **kwargs)


def paginate(request, objects):
    """
    Фукнция для разбивки отображения списка объектов по страницам.
    """
    paginator = Paginator(objects, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


def blog(request):
    """
    Функция, определяющая порядок отображения статей на главной странице блога.
    Добавлена разбивка по страницам. Здесь указано количество статей на страницу.
    Отображаются только те статьи, для которых не была установлена невидимость (черновики).
    """
    content = Article.published.all()
    return render(
        request, "blog/article_list.html", {"page_obj": paginate(request, content)}
    )


def category(request, slug):
    """
    Вывод всех статей, соответствующих определенной категории.
    """
    category = Category.objects.get(slug=slug)
    articles = category.article_set.filter(public=True)
    return render(
        request, "blog/article_list.html", {"page_obj": paginate(request, articles)}
    )


def series(request, slug):
    """
    Вывод всех статей, соответствующих определенной серии.
    """
    series = Series.objects.get(slug=slug)
    articles = series.article_set.filter(public=True)
    return render(
        request, "blog/article_list.html", {"page_obj": paginate(request, articles)}
    )


def topic(request, slug):
    """
    Вывод всех статей, соответствующих определенной теме.
    """
    topic = Topic.objects.get(slug=slug)
    articles = topic.article_set.filter(public=True)
    return render(
        request, "blog/article_list.html", {"page_obj": paginate(request, articles)}
    )
