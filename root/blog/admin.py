from django.contrib import admin
from .models import *

# Register your models here.

class BlogAdmin(admin.ModelAdmin):
    
    fieldsets = [
        ("Содержание", {'fields': ["article_title", "article_content"]}),
        ("Метаданные", {"fields": ["article_slug", "article_theme"]})
    ]

admin.site.register(Theme)
admin.site.register(Article)