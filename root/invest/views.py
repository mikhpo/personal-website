from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def invest(request):
    return render(request = request,
                  template_name='portfolio_optimisation.html',
                  )