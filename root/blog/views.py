from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator
from .models import Article, Comment
from .forms import NewCommentForm

class ArticleDetailView(DetailView):
    model = Article

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        comments_connected = Comment.objects.filter(
            article=self.get_object()).order_by('-posted')
        data['comments'] = comments_connected
        if self.request.user.is_authenticated:
            data['comment_form'] = NewCommentForm(instance=self.request.user)

        return data
    
    def post(self, request, *args, **kwargs):
        new_comment = Comment(content=request.POST.get('content'),
                                  author=self.request.user,
                                  article=self.get_object())
        new_comment.save()
        return self.get(self, request, *args, **kwargs)

# Create your views here.
def blog(request):
    content = Article.objects.filter(visible=True)
    paginator = Paginator(content, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,
                  'blog/index.html',
                  {'page_obj': page_obj})