from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include('main.urls')),
    path('tinymce/', include('tinymce.urls')),
    path("blog/", include('blog.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('apple-touch-icon.png'))),
    path('favicon-32x32.png', RedirectView.as_view(url=staticfiles_storage.url('favicon-32x32.png'))),
    path('favicon-16x16.png', RedirectView.as_view(url=staticfiles_storage.url('favicon-16x16.png'))),
    path('site.webmanifest', RedirectView.as_view(url=staticfiles_storage.url('site.webmanifest'))),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
