from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField('Категория', max_length=100, unique=True)
    description = models.CharField("Описание", max_length=200, blank=True)
    slug = models.SlugField('Ссылка', unique=True)
    image = models.ImageField("Картинка", upload_to='blog/categories/', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField('Тема', max_length=100, unique=True)
    description = models.CharField("Описание", max_length=200, blank=True)
    slug = models.SlugField('Ссылка', unique=True)
    category = models.ManyToManyField(Category, blank=True)
    image = models.ImageField("Картинка", upload_to='blog/topics/', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Темы"

    def __str__(self):
        return self.name

class Series(models.Model):
    name = models.CharField('Серия', max_length=100, unique=True)
    description = models.CharField("Описание", max_length=200, blank=True)
    slug = models.SlugField('Ссылка', unique=True)
    topic = models.ManyToManyField(Topic, blank=True)
    image = models.ImageField("Картинка", upload_to='blog/series/', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Серии"

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField('Заголовок', max_length=100, unique=True)
    description = models.CharField("Описание", max_length=200, blank=True)
    content = models.TextField('Содержание')
    published = models.DateField('Дата публикации', default=now)
    modified = models.DateField('Дата последнего изменения', auto_now=True)
    slug = models.SlugField('Ссылка', unique=True)
    series = models.ManyToManyField(Series, blank=True)
    image = models.ImageField("Картинка", upload_to='blog/articles/', blank=True)
    visible = models.BooleanField("Опубликовано", default=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-published']
        verbose_name_plural = "Статьи"

    def get_absolute_url(self):
        return reverse('blog:article', args=[str(self.slug)])

    def __str__(self):
        return self.title

    @property
    def number_of_comments(self):
        return Comment.objects.filter(article=self).count()

class Comment(models.Model):
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['posted']
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return str(self.author) + ', ' + self.article.title