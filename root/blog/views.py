from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def blogpage(request):
    return HttpResponse("Здесь будет лента блога.")