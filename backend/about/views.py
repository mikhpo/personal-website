"""Представления приложения Обо мне."""

from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Страница "Обо мне".

    Шаблон монтирует React компонент, загружающий данные обо мне из API,
    поэтому представлению достаточно шаблона без контекста.
    """

    template_name = "about/about.html"
