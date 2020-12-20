from django.contrib import admin
from .models import BlogPost

class BlogPostAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Заголовок", {'fields': ["title"]}),
        ("Содержание", {"fields": ["content"]}),
        ('Мета', {'fields': ['themes','published','slug']}),
    ]

admin.site.register(BlogPost, BlogPostAdmin)