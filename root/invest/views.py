from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def optimisation(request):
    return render(request = request,
                  template_name='invest.html',
                  )