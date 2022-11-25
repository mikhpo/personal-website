from django.apps import AppConfig

class BlogConfig(AppConfig):
    name = 'blog'
    verbose_name = "блог"
    default_auto_field = 'django.db.models.AutoField'