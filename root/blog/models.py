from django.db import models
from tinymce.models import HTMLField
from filebrowser.fields import FileBrowseField

class Theme(models.Model):
    name = models.CharField('Тема', max_length=50)

    def __str__(self):
        return self.name
 
class BlogPost(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    content = HTMLField('Содержание')
    image = FileBrowseField("Изображение", max_length=200, directory="images/", extensions=[".jpg"], blank=True)
    document = FileBrowseField("Документ", max_length=200, directory="documents/", extensions=[".pdf",".doc", ".docx", ".xls", ".xlsx", ".xlsm", ".xlsb", ".csv"], blank=True)
    published = models.DateTimeField('Дата публикации', auto_now_add=True)
    theme = models.ManyToManyField(Theme, blank=True)
    slug = models.SlugField(max_length=200, blank=True)

    def __str__(self):
        return self.title