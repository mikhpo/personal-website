from django.contrib import admin
from .models import *

class BlogPostAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Заголовок", {'fields': ["title"]}),
        ("Медиа", {'fields': ["image", "document"]}),
        ("Содержание", {"fields": ["content"]}),
        ('Мета', {'fields': ['theme', 'slug']}),
    ]

class ThemeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Theme, ThemeAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
