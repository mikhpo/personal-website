"""Представления основного модуля проекта."""

from django.templatetags.static import static
from django.views.generic import RedirectView


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
