from django.urls import path
from . import views

app_name = 'scripts'

urlpatterns = [
    path('database-dump/', views.database_dump, name='database_dump'),
]