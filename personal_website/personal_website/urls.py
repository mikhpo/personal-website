"""
Стандартный модуль, в котором зарегистрированы используемые в проекте веб-адреса.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic import RedirectView

from blog.sitemaps import (
    ArticleSitemap,
    CategorySitemap,
    SeriesSitemap,
    TopicSitemap,
)
from gallery.sitemaps import AlbumSitemap, PhotoSitemap, TagSitemap

sitemaps = {
    "articles": ArticleSitemap,
    "series": SeriesSitemap,
    "topics": TopicSitemap,
    "categories": CategorySitemap,
    "photos": PhotoSitemap,
    "albums": AlbumSitemap,
    "tags": TagSitemap,
}

urlpatterns = [
    path("", RedirectView.as_view(url="main/", permanent=True)),
    path("tinymce/", include("tinymce.urls")),
    path("admin/", admin.site.urls, name="admin"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    path("main/", include("main.urls")),
    path("blog/", include("blog.urls")),
    path("gallery/", include("gallery.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
