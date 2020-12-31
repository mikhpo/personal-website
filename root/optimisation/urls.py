from django.urls import path
from . import views


app_name = 'optimisation'  # here for namespacing of urls.

urlpatterns = [
    path("optimisation/", views.optimisation, name="optimisation"),
]