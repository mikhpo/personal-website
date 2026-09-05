"""Кастомные фильтры поиска для REST API."""

import operator
from functools import reduce
from typing import TYPE_CHECKING, ClassVar

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import connection
from rest_framework import filters
from rest_framework.request import Request
from rest_framework.views import APIView

if TYPE_CHECKING:
    from django.db.models import QuerySet

# Веса полей поиска по позиции: первое поле в search_fields важнее последующих.
SEARCH_WEIGHTS: tuple[str, ...] = ("A", "B", "C", "D")


class DatabaseSearchFilter(filters.SearchFilter):
    """
    Поисковый фильтр с полнотекстовым поиском PostgreSQL.

    На PostgreSQL (connection.vendor == "postgresql") параметр search
    обрабатывается через SearchQuery с конфигурацией "russian" (морфология
    словоформ): по полям view.search_fields строится SearchVector, набор
    фильтруется по полнотекстовому совпадению и сортируется по релевантности
    (SearchRank), затем по ordering вьюхи. На остальных СУБД (SQLite в CI)
    работает поведение родителя - icontains.
    """

    search_config: ClassVar[str] = "russian"

    def filter_queryset(self, request: Request, queryset: "QuerySet", view: APIView) -> "QuerySet":
        """
        Отфильтровать queryset по поисковому запросу с сортировкой по релевантности.

        Args:
            request: HTTP запрос
            queryset: Исходный набор данных
            view: APIView, обрабатывающий запрос

        Returns:
            Отфильтрованный и ранжированный набор данных
        """
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)
        if connection.vendor != "postgresql" or not search_fields or not search_terms:
            return super().filter_queryset(request, queryset, view)

        # Векторы полей складываются (reduce по operator.add дает цепочку
        # v1 + v2 + ...), образуя единый вектор: совпадение ищется по всем
        # полям search_fields одновременно. Веса берутся из SEARCH_WEIGHTS по
        # позиции поля: чем раньше поле, тем больший вклад его совпадение
        # вносит в rank, поэтому статья с совпадением в заголовке (вес A)
        # оказывается выше статьи с равным по частоте совпадением в описании.
        # strict=False допускает меньшее число полей, чем весов.
        vector = reduce(
            operator.add,
            (
                SearchVector(field, weight=weight, config=self.search_config)
                for field, weight in zip(search_fields, SEARCH_WEIGHTS, strict=False)
            ),
        )

        # Запрос строится с той же конфигурацией, что и вектор: слова
        # приводятся к начальным формам, поэтому "статья" находит "статьи".
        query = SearchQuery(" ".join(search_terms), config=self.search_config)

        # annotate вычисляет rank (релевантность) для каждой строки, filter
        # оставляет строки с полнотекстовым совпадением вектора и запроса,
        # "-rank" сортирует по убыванию релевантности, ordering вьюхи служит
        # дополнительной сортировкой при равном rank.
        return (
            queryset.annotate(search=vector, rank=SearchRank(vector, query))
            .filter(search=query)
            .order_by("-rank", *getattr(view, "ordering", []))
        )
