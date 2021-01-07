from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator
from .models import Article

class ArticleDetailView(DetailView):
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# Create your views here.
def blog(request):
    content = Article.objects.filter(draft=False)
    paginator = Paginator(content, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,
                  'blog/articles_list.html',
                  {'page_obj': page_obj})