"""Представления основного модуля проекта."""

from django.db import connection
from django.db.utils import DatabaseError
from django.http import HttpRequest, HttpResponse
from django.templatetags.static import static
from django.views.generic import RedirectView, View


class HealthView(View):
    """Проверка живости приложения и соединения с базой данных.

    Единая точка живости для всех режимов запуска: healthcheck контейнера,
    проверка после развертывания, внешний мониторинг. Выполняет тривиальный
    запрос к базе данных, не требует аутентификации и не выполняет
    перенаправлений.
    """

    def get(self, request: HttpRequest) -> HttpResponse:  # noqa: ARG002
        """
        Выполнить проверочный запрос к базе данных.

        Args:
            request (HttpRequest): HTTP-запрос проверки (не используется).

        Returns:
            HttpResponse: Тело "ok" со статусом 200 при доступной базе данных,
            статус 503 при ошибке выполнения запроса.
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except DatabaseError:
            return HttpResponse("unavailable", status=503)
        return HttpResponse("ok")


class StaticRedirectView(RedirectView):
    """Постоянный редирект запроса на статический файл.

    Целевой адрес вычисляется в момент запроса через текущее хранилище
    статических файлов, поэтому корректен для любого режима раздачи статики:
    WhiteNoise локально, объектное хранилище в продуктиве.
    """

    permanent = True

    # Путь до статического файла (устанавливается через as_view).
    static_path = ""

    def __init__(self, static_path: str = "", **kwargs) -> None:
        """
        Инициализация представления путём до статического файла.

        Args:
            static_path (str): Относительный путь до статического файла.
            **kwargs: Прочие аргументы базового представления.
        """
        self.static_path = static_path
        super().__init__(**kwargs)

    def get_redirect_url(self, *args: object, **kwargs: object) -> str:  # noqa: ARG002
        """
        Возвращает адрес статического файла для перенаправления.

        Args:
            *args: Позиционные аргументы запроса.
            **kwargs: Именованные аргументы запроса.

        Returns:
            str: Абсолютный или относительный адрес статического файла.
        """
        return static(self.static_path)
