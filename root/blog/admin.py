from django.contrib import admin
from .models import *
from tinymce.widgets import TinyMCE

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    '''
    Настройки отображения модели статьи в панели администрирования Django.
    '''
    model = Article
    
    list_display = ('title', 'published', 'modified', 'visible')
    list_filter = ('series', 'visible')

    fieldsets = (
        ("Содержание", {'fields': ["title", "description", "content"]}),
        ("Метаданные", {"fields": ["series"]}),
        ("Картинка", {'fields': ["image"]}),
        ("Служебные", {"fields": ["slug", "visible", "published"]}),
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

admin.site.register(Comment)
admin.site.register(Series)
admin.site.register(Topic)
admin.site.register(Category)