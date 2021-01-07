from django.db import models
from tinymce.models import HTMLField
from django.urls import reverse  # To generate URLS by reversing URL patterns
from django.utils.timezone import now

# Create your models here.

class Topic(models.Model):
    name = models.CharField('Тема', max_length=200, unique=True)
    description = models.CharField("Описание", max_length=200, blank=True)
    slug = models.SlugField('Ссылка', unique=True)
    image = models.ImageField("Картинка", upload_to='blog/topics/', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Темы"

    def __str__(self):
        return self.name

class Series(models.Model):
    name = models.CharField('Серия', max_length=200, unique=True)
    description = models.CharField("Описание", max_length=200, blank=True)
    slug = models.SlugField('Ссылка', unique=True)
    image = models.ImageField("Картинка", upload_to='blog/series/', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Серии"

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField('Заголовок', max_length=200, unique=True)
    content = HTMLField('Содержание')
    description = models.CharField("Описание", max_length=200, blank=True)
    published = models.DateField('Дата публикации', default=now)
    modified = models.DateField('Дата последнего изменения', auto_now=True)
    slug = models.SlugField('Ссылка', unique=True)
    topic = models.ManyToManyField(Topic, blank=True)
    series = models.ManyToManyField(Series, blank=True)
    image = models.ImageField("Картинка", upload_to='blog/articles/', blank=True)
    draft = models.BooleanField("Черновик", default=False)

    class Meta:
        ordering = ['-published']
        verbose_name_plural = "Статьи"

    def get_absolute_url(self):
        return reverse('blog:article', args=[str(self.slug)])

    def __str__(self):
        return self.title