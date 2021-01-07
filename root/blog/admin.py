from django.contrib import admin
from django.utils.safestring import mark_safe 
from .models import *

# Register your models here.

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    model = Article
    
    list_display = ('title', 'published', 'modified', 'draft')
    list_filter = ('topic', 'series', 'draft')

    fieldsets = (
        ("Содержание", {'fields': ["title", "description", "content"]}),
        ("Метаданные", {"fields": [("topic", "series")]}),
        ("Служебные", {"fields": ["slug", "draft"]}),
        ("Картинка", {'fields': ["image"]}),
        ("Дата", {'fields': ["published"]}),
    )

    readonly_fields=('published',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["published"]
        else:
            return []

admin.site.register(Topic)
admin.site.register(Series)