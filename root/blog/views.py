from django.shortcuts import render
from django.http import HttpResponse
from .models import BlogPost


# Create your views here.
def blogpage(request):
    latest_blogposts_list = BlogPost.objects.order_by('published')[:5]
    context = {'latest_blogposts_list': latest_blogposts_list}
    return render(request, 'index.html', context)