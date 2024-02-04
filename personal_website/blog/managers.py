"""Менеджеры блога."""
from personal_website.managers import PublicManager


class PublicArticleManager(PublicManager):
    """Менеджер для работы с публичными статьями."""


class PublicSeriesManager(PublicManager):
    """Менеджер для работы с публичными сериями."""


class PublicTopicManager(PublicManager):
    """Менеджер для работы с публичными темами."""


class PublicCategoryManager(PublicManager):
    """Менеджер для работы с публичными категориями."""
