from django.shortcuts import render
from apps.blog.models import Category, Series

def main(request):
    categories = Category.objects.filter(public=True).exclude(image='')
    series = Series.objects.filter(public=True).exclude(image='')
    return render(
        request,
        'main/main.html',
        {
            "categories": categories,
            "series": series
        }
    )