from django.urls import path
from . import views


app_name = 'invest'  # here for namespacing of urls.

urlpatterns = [
    path("invest/", views.optimisation, name="invest"),
]