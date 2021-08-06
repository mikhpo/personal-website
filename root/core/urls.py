# Стандартный модуль, в котором зарегистрированы используемые в проекте веб-адреса.

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import ArticleSitemap, CategorySitemap, SeriesSitemap, Topic, Category, TopicSitemap
from django.views.generic import RedirectView

sitemaps = {
    'articles': ArticleSitemap,
    'series': SeriesSitemap,
    'topics': TopicSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    path("", RedirectView.as_view(url='main/', permanent=True)),
    path("main/", include('main.urls')),
    path('tinymce/', include('tinymce.urls')),
    path("blog/", include('blog.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('scripts/', include('scripts.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
