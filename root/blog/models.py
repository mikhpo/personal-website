from django.db import models
from django.utils.timezone import now
from tinymce.models import HTMLField
from multiselectfield import MultiSelectField

themes = (
        ("photo", "Фотография"),
        ("travel", "Путешествия"),
        ("books", "Книги"),
        ("movies", "Кино"),
        ("games", "Игры"),
        ("development", "Разработка"),
        ("ML", "Машинное обучение"),
        ("finance", "Финансы"),
        ("investment", "Инвестиции"),
)
 
class BlogPost(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    content = HTMLField('Содержание')
    published = models.DateField('Дата публикации', default=now())
    themes = MultiSelectField(choices=themes, blank=True)
    slug = models.SlugField(max_length=200, blank=True)

    def __str__(self):
        return self.title