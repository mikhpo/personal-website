from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = "blog"
    verbose_name = "Блог"
    default_auto_field = "django.db.models.AutoField"
