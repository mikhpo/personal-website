from django.shortcuts import render
from django.http import HttpResponse
from .models import Article

# Create your views here.
def blogpage(request):
    return render(request = request,
                  template_name='blog.html',
                  context = {"articles":Article.objects.all})