'''Стандартный модуль, в котором зарегистрированы используемые в проекте веб-адреса.'''

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import RedirectView
from blog.sitemaps import ArticleSitemap, CategorySitemap, SeriesSitemap, TopicSitemap
from personal_website.settings import MEDIA_URL, MEDIA_ROOT

sitemaps = {
    'articles': ArticleSitemap,
    'series': SeriesSitemap,
    'topics': TopicSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    path("", RedirectView.as_view(url='main/', permanent=True)),
    path('tinymce/', include('tinymce.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path("main/", include('main.urls')),
    path("blog/", include('blog.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
] 

urlpatterns = urlpatterns + static(MEDIA_URL, document_root=MEDIA_ROOT)