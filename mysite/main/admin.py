from django.contrib import admin
from .models import BlogPost


class BlogPostAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Заголовок и дата публикации", {'fields': ["BlogPost_title", "BlogPost_published"]}),
        ("Содержание", {"fields": ["BlogPost_content"]})
    ]

admin.site.register(BlogPost, BlogPostAdmin)