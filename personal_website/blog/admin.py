from django.contrib import admin
from tinymce.widgets import TinyMCE
from .models import *


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    '''
    Настройки отображения модели статьи в панели администрирования Django.
    '''
    model = Article
    
    list_display = ('title', 'published', 'modified', 'public')
    list_filter = ('series', 'topic', 'category', 'public')

    fieldsets = (
        ("Содержание", {'fields': ["title", "description", "content"]}),
        ("Метаданные", {"fields": ["series", "topic", "category"]}),
        ("Картинка", {'fields': ["image"]}),
        ("Служебные", {"fields": ["slug", "public", "published"]}),
    )

    # Стандартная форма тектового поля заменена на HTML форму TinyMCE.
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
        }

    # Дату публикации можно изменить только при создании статьи, но не при редактировании.
    readonly_fields=('published',)

    # Автор фиксируется, но не редактируется.
    exclude = ('author',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["published"]
        else:
            return []

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    '''
    Настройки отображения модели категории в панели администрирования Django.
    '''
    model = Category
    list_display = ('name', 'public', 'slug', 'image')
    list_filter = ('public',)

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    '''
    Настройки отображения модели серии в панели администрирования Django.
    '''
    model = Series
    list_display = ('name', 'public', 'slug', 'image')
    list_filter = ('public',)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    '''
    Настройки отображения модели тем в панели администрирования Django.
    '''
    model = Topic
    list_display = ('name', 'public', 'slug', 'image')
    list_filter = ('public',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    '''
    Настройки отображения модели комментариев в панели администрирования Django.
    '''
    model = Comment
    list_display = ('article', 'author', 'posted')
    list_filter = ('article', 'author')