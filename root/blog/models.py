from django.db import models

# Create your models here.

class Theme(models.Model):
    name = models.CharField('Тема', max_length=200)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Article(models.Model):
    article_title = models.CharField('Заголовок', max_length=200)
    article_content = models.TextField('Содержание')
    article_published = models.DateTimeField('Дата публикации', auto_now_add=True)
    article_modified = models.DateTimeField('Дата последнего изменения', auto_now=True)
    article_slug = models.SlugField('Ссылка')
    article_theme = models.ManyToManyField(Theme)

    class Meta:
        ordering = ['-article_published']

    def __str__(self):
        return self.article_title

