# Стандартный модуль, в котором зарегистрированы используемые в проекте веб-адреса.

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import RedirectView
from apps.blog.sitemaps import ArticleSitemap, CategorySitemap, SeriesSitemap, TopicSitemap

sitemaps = {
    'articles': ArticleSitemap,
    'series': SeriesSitemap,
    'topics': TopicSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    path("", RedirectView.as_view(url='main/', permanent=True)),
    path("main/", include('apps.main.urls')),
    path('tinymce/', include('tinymce.urls')),
    path("blog/", include('apps.blog.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('scripts/', include('apps.scripts.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
