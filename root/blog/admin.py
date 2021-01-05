from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'modified', 'visible')
    list_filter = ('topic', 'series', 'visible')

    fieldsets = (
        ("Содержание", {'fields': ["title", "content"]}),
        ("Метаданные", {"fields": [("topic", "series")]}),
        ("Служебные", {"fields": ["slug", "visible"]}),
    )

admin.site.register(Topic)
admin.site.register(Series)