from django.urls import path
from django.views.generic import RedirectView


app_name = 'main'

urlpatterns = [
    path("", RedirectView.as_view(url='blog/', permanent=True), name='main'),
]