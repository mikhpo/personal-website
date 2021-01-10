from django.urls import path
from django.views.generic import RedirectView


app_name = 'main'  # here for namespacing of urls.

urlpatterns = [
    path("", RedirectView.as_view(url='blog/', permanent=True), name='main'),
]