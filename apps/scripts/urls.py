from django.urls import path
from . import views

app_name = 'scripts'

urlpatterns = [
    path('', views.jobs, name='scripts'),
    path('command/<slug:slug>/', views.command, name='command'),
    path('jobs/', views.jobs, name='jobs'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('executions/', views.executions, name='executions')
]