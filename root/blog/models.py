from django.db import models
from tinymce.models import HTMLField

class Theme(models.Model):
    name = models.CharField('Тема', max_length=50)

    def __str__(self):
        return self.name
 
class BlogPost(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    content = HTMLField('Содержание')
    published = models.DateTimeField('Дата публикации', auto_now_add=True)
    theme = models.ManyToManyField(Theme, blank=True)
    slug = models.SlugField(max_length=200, blank=True)

    def __str__(self):
        return self.title