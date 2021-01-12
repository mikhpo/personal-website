from django.shortcuts import render

def main(request):
    return render(request = request,
                  template_name='main.html',
                  )