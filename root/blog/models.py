from django.db import models
from tinymce.models import HTMLField
from django.urls import reverse  # To generate URLS by reversing URL patterns

# Create your models here.

class Topic(models.Model):
    name = models.CharField('Тема', max_length=200, unique=True)
    slug = models.SlugField('Ссылка', unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Темы"

    def __str__(self):
        return self.name

class Series(models.Model):
    name = models.CharField('Серия', max_length=200, unique=True)
    slug = models.SlugField('Ссылка', unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Серии"

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField('Заголовок', max_length=200, unique=True)
    content = HTMLField('Содержание')
    published = models.DateTimeField('Дата публикации', auto_now_add=True)
    modified = models.DateTimeField('Дата последнего изменения', auto_now=True)
    slug = models.SlugField('Ссылка', unique=True)
    topic = models.ManyToManyField(Topic, blank=True)
    series = models.ManyToManyField(Series, blank=True)
    visible = models.BooleanField("Статья видима", default=True)

    class Meta:
        ordering = ['-published']
        verbose_name_plural = "Статьи"

    def get_absolute_url(self):
        return reverse('article', args=[str(self.slug)])

    def __str__(self):
        return self.title