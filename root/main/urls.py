from django.conf.urls import url
from django.urls import path
from . import views
from django.views.generic import RedirectView


app_name = 'main'  # here for namespacing of urls.

urlpatterns = [
    path("", RedirectView.as_view(url='blog/', permanent=True)),
]