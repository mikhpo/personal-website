"""URL конфигурация для централизированного API."""

from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from accounts.urls import router as accounts_router
from gallery.urls import router as gallery_router

app_name = "api"

urlpatterns = [
    path("", RedirectView.as_view(url="/api/docs/", permanent=False), name="api_root"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", RedirectView.as_view(url="/api/docs/swagger/", permanent=False), name="docs"),
    path("docs/swagger/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="swagger"),
    path("docs/redoc/", SpectacularRedocView.as_view(url_name="api:schema"), name="redoc"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("accounts/", include(accounts_router.urls)),
    path("gallery/", include(gallery_router.urls)),
]
