# Стандартный модуль, в котором зарегистрированы используемые в проекте веб-адреса.

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include('main.urls')),
    path('tinymce/', include('tinymce.urls')),
    path("blog/", include('blog.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('scripts/', include('scripts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
