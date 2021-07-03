from django.urls import path
from . import views

app_name = 'scripts'

urlpatterns = [
    path('database_dump/', views.database_dump, name='database_dump'),
]