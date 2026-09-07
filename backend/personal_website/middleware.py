"""Промежуточное ПО для журналирования отказов в доступе."""

import logging
from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(settings.PROJECT_NAME)


class SecurityLogMiddleware:
    """Журналирует ответы с кодами 401 и 403.

    Записывает событие отказа с пользователем, IP-адресом, методом и путем
    запроса. Исключает эндпоинты аутентификации: их события фиксируются
    сигналами авторизации в accounts/signals.py, иначе в журнале
    дублируются записи о неудачных попытках входа.
    """

    excluded_prefixes: tuple[str, ...] = ("/api/auth/",)

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Сохранить следующий обработчик цепочки промежуточного ПО."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Журналировать ответ при отказе в доступе."""
        response = self.get_response(request)
        if response.status_code in (401, 403) and not request.path.startswith(self.excluded_prefixes):
            user = getattr(request, "user", None)
            username = user.username if user and user.is_authenticated else "аноним"
            ip = request.META.get("HTTP_X_REAL_IP")
            logger.warning(
                f"Отказ доступа: {request.method} {request.path} пользователь {username} с IP-адреса {ip}",
            )
        return response
