"""Модели блога."""

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from blog.managers import PublicArticleManager, PublicCategoryManager, PublicSeriesManager, PublicTopicManager
from personal_website.utils import get_unique_slug


class Category(models.Model):
    """Модель тематической категории статьи в блоге.

    Примеры:
    - Разработка
    - Путешествия
    """

    name = models.CharField("Категория", max_length=255, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True)
    slug = models.SlugField("Слаг", blank=True, unique=True)
    image = models.ImageField("Картинка", upload_to="blog/categories/", blank=True)
    public = models.BooleanField("Опубликовано", default=False)

    objects = models.Manager()
    published = PublicCategoryManager()

    class Meta:  # noqa: D106
        ordering = ("name",)
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        """Строкое представление категории возвращает название категории."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Если слаг категории не указан, то слаг определяется из названия категории."""
        if not self.slug:
            self.slug = get_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Абсолютная ссылка на категорию содержит слаг категории."""
        return reverse("blog:category", args=[str(self.slug)])


class Topic(models.Model):
    """Модель темы статьи в блоге.

    Примеры:
    - Горы
    - Дети
    """

    name = models.CharField("Тема", max_length=255, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True)
    slug = models.SlugField("Слаг", blank=True, unique=True)
    image = models.ImageField("Картинка", upload_to="blog/topics/", blank=True)
    public = models.BooleanField("Опубликовано", default=False)

    objects = models.Manager()
    published = PublicTopicManager()

    class Meta:  # noqa: D106
        ordering = ("name",)
        verbose_name_plural = "Темы"

    def __str__(self) -> str:
        """Строковое представление темы возвращает название темы."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Если слаг не был указан, то слаг определяется из названия темы."""
        if not self.slug:
            self.slug = get_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Абсолютная ссылка на тему включает в себя слаг темы."""
        return reverse("blog:topic", args=[str(self.slug)])


class Series(models.Model):
    """Модель серии статей в блоге.

    Примеры:
    - Лангтанг-трек
    - Путешествие по осенней Тоскане
    """

    name = models.CharField("Серия", max_length=255, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True)
    slug = models.SlugField("Слаг", blank=True, unique=True)
    image = models.ImageField("Картинка", upload_to="blog/series/", blank=True)
    public = models.BooleanField("Опубликовано", default=False)

    objects = models.Manager()
    published = PublicSeriesManager()

    class Meta:  # noqa: D106
        ordering = ("name",)
        verbose_name_plural = "Серии"

    def __str__(self) -> str:
        """Строкое представление серии совпадает с названием серии."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Если слаг серии не был указан, то слаг определиться автоматически по назанию."""
        if not self.slug:
            self.slug = get_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Абсолютная ссылка на серию содержит слаг серии."""
        return reverse("blog:series", args=[str(self.slug)])


class Article(models.Model):
    """Модель статьи в блоге.

    Статья может быть связана с одной или несколькими сериями, темами и категориями.
    У статьи может быть один автор.
    """

    title = models.CharField("Заголовок", max_length=255, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True)
    content = models.TextField("Содержание")
    published_at = models.DateTimeField("Дата публикации", blank=True, null=True, default=now)
    modified_at = models.DateTimeField("Дата последнего изменения", auto_now=True)
    slug = models.SlugField("Слаг", blank=True, unique=True)
    series = models.ManyToManyField(Series, blank=True)
    topics = models.ManyToManyField(Topic, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    image = models.ImageField("Картинка", upload_to="blog/articles/", blank=True)
    public = models.BooleanField("Опубликовано", default=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    objects = models.Manager()
    published = PublicArticleManager()

    class Meta:  # noqa: D106
        ordering = ("-published_at",)
        verbose_name_plural = "Статьи"

    def __str__(self) -> str:
        """Строковое представление статьи возвращает заголовок."""
        return self.title

    def save(self, *args, **kwargs) -> None:
        """Если слаг не указан, то слаг определяется автоматически по заголовку."""
        if not self.slug:
            self.slug = get_unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Абсолютная ссылка на статью определяется слагом статьи."""
        return reverse("blog:article", args=[str(self.slug)])

    @property
    def number_of_comments(self) -> int:
        """Количество комментариев."""
        return Comment.objects.filter(article=self).count()


class Comment(models.Model):
    """Модель комментария к статье.

    Комментарий связан с одной статьей и с одним пользователем.
    У одной статьи может быть много комментариев.
    """

    article = models.ForeignKey(Article, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    posted = models.DateTimeField(auto_now_add=True)

    class Meta:  # noqa: D106
        ordering = ("posted",)
        verbose_name_plural = "Комментарии"

    def __str__(self) -> str:
        """Строкое представление комментрия содержит автора комментария и статью, к которой был оставлен комментарий."""
        return f"{self.author}, {self.article.title}"
