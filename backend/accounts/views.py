"""Представления для системы авторизации пользователей."""

import logging
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect, render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.forms import SignUpForm

logger = logging.getLogger(settings.PROJECT_NAME)


class TokenObtainPairLoggingView(TokenObtainPairView):
    """Выдача JWT-токена с журналированием успешной аутентификации.

    SimpleJWT не вызывает django.contrib.auth.login(), поэтому сигнал
    user_logged_in при выдаче токена не срабатывает: без этого
    представления успешные входы через API не попадают в журнал.
    """

    def post(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """Выдать пару токенов и записать событие в журнал."""
        response = super().post(request, *args, **kwargs)
        if response.status_code == HTTPStatus.OK:
            username = request.data.get("username")
            ip = request.META.get("HTTP_X_REAL_IP")
            logger.info(f"Выдан JWT-токен пользователю {username} с IP-адреса {ip}")
        return response


def signup(request: HttpRequest) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    """
    Представление для регистрации нового пользователя.
    После завершения регистрации автоматически происходит авторизация.
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            ip = request.META.get("HTTP_X_REAL_IP")
            logger.info(f"Зарегистрирован пользователь {user.username} с IP-адреса {ip}")
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("main:main")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})
