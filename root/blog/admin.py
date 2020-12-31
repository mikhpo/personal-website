from django.contrib import admin
from .models import *

# Register your models here.

class BlogAdmin(admin.ModelAdmin):
    
    fieldsets = [
        ("Содержание", {'fields': ["article_title", "article_content"]}),
        ("Метаданные", {"fields": ["article_slug", "article_topic", "article_series"]})
    ]

admin.site.register(Topic)
admin.site.register(Series)
admin.site.register(Article)