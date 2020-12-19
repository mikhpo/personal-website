from django.db import models
from django.utils.timezone import now
from tinymce.models import HTMLField



class BlogPost(models.Model):
    BlogPost_title = models.CharField('Заголовок', max_length=200)
    BlogPost_content = HTMLField('Содержание')
    BlogPost_published = models.DateField('Дата публикации', default=now().date())

    def __str__(self):
        return self.BlogPost_title