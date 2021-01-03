from django.db import models
from tinymce.models import HTMLField

# Create your models here.

class Topic(models.Model):
    topic_name = models.CharField('Тема', max_length=200)
    topic_slug = models.SlugField('Ссылка')

    class Meta:
        ordering = ['topic_name']
        verbose_name_plural = "Темы"

    def __str__(self):
        return self.topic_name

class Series(models.Model):
    series_name = models.CharField('Серия', max_length=200)
    series_slug = models.SlugField('Ссылка')

    class Meta:
        ordering = ['series_name']
        verbose_name_plural = "Серии"

    def __str__(self):
        return self.series_name

class Article(models.Model):
    article_title = models.CharField('Заголовок', max_length=200)
    article_content = HTMLField('Содержание')
    article_published = models.DateTimeField('Дата публикации', auto_now_add=True)
    article_modified = models.DateTimeField('Дата последнего изменения', auto_now=True)
    article_slug = models.SlugField('Ссылка')
    article_theme = models.ManyToManyField(Topic)
    article_series = models.ManyToManyField(Series, blank=True)

    class Meta:
        ordering = ['-article_published']
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.article_title

class Author(models.Model):
    author_name=

