"""Представления для системы авторизации пользователей."""
from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect, render

from accounts.forms import SignUpForm


def signup(request: HttpRequest) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
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
