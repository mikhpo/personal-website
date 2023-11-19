from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from utils import get_unique_slug

from .managers import (
    PublicArticleManager,
    PublicGategoryManager,
    PublicSeriesManager,
    PublicTopicManager,
)


class Category(models.Model):
    """
    Модель тематической категории.
    """

    name = models.CharField("Категория", max_length=255, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True)
    slug = models.SlugField("Слаг", blank=True, unique=True)
    image = models.ImageField("Картинка", upload_to="blog/categories/", blank=True)
    public = models.BooleanField("Опубликовано", default=False)

    objects = models.Manager()
    published = PublicGategoryManager()

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Topic(models.Model):
    """
    Модель темы.
    Тема может относиться к нескольким категориям.
    """

    name = models.CharField("Тема", max_length=255, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True)
    slug = models.SlugField("Слаг", blank=True, unique=True)
    image = models.ImageField("Картинка", upload_to="blog/topics/", blank=True)
    public = models.BooleanField("Опубликовано", default=False)

    objects = models.Manager()
    published = PublicTopicManager()

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Темы"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:topic", args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Series(models.Model):
    """
    Модель серии.
    Серия может быть на несколько тем.
    """

    name = models.CharField("Серия", max_length=255, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True)
    slug = models.SlugField("Слаг", blank=True, unique=True)
    image = models.ImageField("Картинка", upload_to="blog/series/", blank=True)
    public = models.BooleanField("Опубликовано", default=False)

    objects = models.Manager()
    published = PublicSeriesManager()

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Серии"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:series", args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    """
    Модель статьи.
    Статья может быть частью серии.
    Статья связана с одним пользователем.
    """

    title = models.CharField("Заголовок", max_length=255, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True)
    content = models.TextField("Содержание")
    published_at = models.DateTimeField(
        "Дата публикации", blank=True, null=True, default=now
    )
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

    class Meta:
        ordering = ["-published_at"]
        verbose_name_plural = "Статьи"

    def get_absolute_url(self):
        return reverse("blog:article", args=[str(self.slug)])

    def __str__(self):
        return self.title

    @property
    def number_of_comments(self):
        return Comment.objects.filter(article=self).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, self.title)
        super().save(*args, **kwargs)


class Comment(models.Model):
    """
    Модель комментария к статье.
    Комментарий связан с одной статьей и с одним пользователем.
    У одной статьи может быть много комментариев.
    """

    article = models.ForeignKey(
        Article, related_name="comments", on_delete=models.CASCADE
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["posted"]
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return str(self.author) + ", " + self.article.title
