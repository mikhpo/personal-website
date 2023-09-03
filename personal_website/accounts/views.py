from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from .forms import SignUpForm


def signup(request):
    """
    Представление для регистрации нового пользователя.
    После завершения регистрации автоматически происходит авторизация.
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("main:main")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})
