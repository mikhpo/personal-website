from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def mainpage(request):
    return HttpResponse("Здравствуй, мир! Это стартовая страница.")