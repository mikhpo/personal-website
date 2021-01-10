from django.contrib import admin
from .models import *
from tinymce.widgets import TinyMCE

# Register your models here.

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    model = Article
    
    list_display = ('title', 'published', 'modified', 'visible')
    list_filter = ('series', 'visible')

    fieldsets = (
        ("Содержание", {'fields': ["title", "description", "content"]}),
        ("Метаданные", {"fields": ["series"]}),
        ("Картинка", {'fields': ["image"]}),
        ("Служебные", {"fields": ["slug", "visible", "published"]}),
    )

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
        }

    readonly_fields=('published',)

    exclude = ('author',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["published"]
        else:
            return []

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.added_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Comment)
admin.site.register(Series)
admin.site.register(Topic)
admin.site.register(Category)