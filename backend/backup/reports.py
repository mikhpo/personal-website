"""Отчеты о результатах резервного копирования.

HTML-отчет по согласованному макету собирается шаблоном Django
templates/backup/email_report.html: бейдж статуса, таблица-шапка, разделы БД
и медиа, при ошибке - полный журнал команды. Отправка штатным django
send_mail. Команды backup, backup_db и backup_media вызывают
run_with_report для реальных запусков; проверка целей (--verify)
уведомлений не создает. Ошибка отправки не меняет код возврата команды -
пишется предупреждение.
"""

import io
import logging
import socket
import sys
import time
from collections.abc import Callable
from contextlib import redirect_stderr
from datetime import datetime
from typing import Any, TextIO

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import CommandError
from django.template.loader import render_to_string
from typing_extensions import Self

from backup.utils import BYTES_PER_KIB, now_local

logger = logging.getLogger(__name__)

PROJECT_NAME = "personal-website"
REPORT_TEMPLATE = "backup/email_report.html"
STATUS_OK = "успех"
STATUS_FAIL = "ОШИБКА"
SIZE_UNITS = ("Б", "КБ", "МБ", "ГБ")


class JournalCollector(logging.Handler):
    """Собирает записи журнала резервного копирования в список строк."""

    def __init__(self, lines: list[str]) -> None:
        """Настроить уровень записи и приемник строк.

        Args:
            lines (list[str]): Список, куда попадают отформатированные записи.
        """
        super().__init__(level=logging.INFO)
        self.lines = lines

    def emit(self, record: logging.LogRecord) -> None:
        """Добавить запись в список в виде "LEVEL сообщение"."""
        self.lines.append(f"{record.levelname} {record.getMessage()}")


class StderrTee(io.TextIOBase):
    """Дублирует записи в stderr: исходный поток получает текст как раньше,
    список строк журнала - непустые строки.
    """

    def __init__(self, original: TextIO, lines: list[str]) -> None:
        """Сохранить исходный поток и приемник строк.

        Args:
            original (TextIO): Настоящий stderr, дублирующий вывод.
            lines (list[str]): Список строк общего журнала.
        """
        self.original = original
        self.lines = lines

    def write(self, text: str) -> int:
        """Записать текст в исходный поток и в журнал.

        Args:
            text (str): Записываемый текст (может быть многострочным).

        Returns:
            int: Число записанных символов.
        """
        self.original.write(text)
        self.lines.extend(line for line in text.splitlines() if line.strip())
        return len(text)

    def flush(self) -> None:
        """Сбросить буфер исходного потока."""
        self.original.flush()


class JournalCapture:
    """Перехват журнала команды на время работы блока with.

    Записи логгеров "backup" и вывод внешних команд в stderr попадают
    в lines в порядке поступления; по выходу из блока прежний уровень
    логгера и stderr восстанавливаются.

    Attributes:
        lines (list[str]): Строки журнала, собранные внутри блока with.
    """

    def __init__(self) -> None:
        """Создать перехватчик; активация происходит входом в блок with."""
        self.lines: list[str] = []
        self._collector = JournalCollector(self.lines)
        self._logger: logging.Logger | None = None
        self._logger_level: int | None = None
        self._stderr_redirector: Any = None

    def __enter__(self) -> Self:
        """Подключить сбор журнала и подменить stderr.

        Returns:
            JournalCapture: Этот перехватчик со списком lines.
        """
        self._logger = logging.getLogger("backup")
        self._logger_level = self._logger.level
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(self._collector)
        self._stderr_redirector = redirect_stderr(StderrTee(sys.stderr, self.lines))
        self._stderr_redirector.__enter__()
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Восстановить stderr, уровень и состав обработчиков логгера."""
        self._stderr_redirector.__exit__(exc_type, exc_value, traceback)
        if self._logger is not None and self._logger_level is not None:
            self._logger.removeHandler(self._collector)
            self._logger.setLevel(self._logger_level)


def format_size(size_bytes: int) -> str:
    """Объем в человекочитаемом виде: русская десятичная запятая и единицы Б-ГБ.

    Args:
        size_bytes (int): Размер в байтах.

    Returns:
        str: Строка вида "1,4 МБ"; значения меньше килобайта - "5,0 Б".

    Example:
        >>> format_size(1468006)
        '1,4 МБ'
    """
    value = float(size_bytes)
    unit_index = 0
    while value >= BYTES_PER_KIB and unit_index < len(SIZE_UNITS) - 1:
        value /= BYTES_PER_KIB
        unit_index += 1
    return f"{value:.1f}".replace(".", ",") + f" {SIZE_UNITS[unit_index]}"


def format_count(count: int) -> str:
    """Число с пробелами между разрядами.

    Args:
        count (int): Число объектов.

    Returns:
        str: Строка вида "6 707".

    Example:
        >>> format_count(6707)
        '6 707'
    """
    return f"{count:,}".replace(",", " ")


def format_duration(seconds: float) -> str:
    """Длительность в виде "12 мин 34 с"; часы добавляются при превышении часа.

    Args:
        seconds (float): Длительность в секундах.

    Returns:
        str: Строка вида "12 мин 34 с".

    Example:
        >>> format_duration(42)
        '0 мин 42 с'
    """
    total = round(seconds)
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    parts = [f"{hours} ч"] if hours else []
    parts += [f"{minutes} мин", f"{secs} с"]
    return " ".join(parts)


def report_subject(command: str, status: str, started: datetime) -> str:
    """Тема письма по макету.

    Args:
        command (str): Имя команды ("backup_db").
        status (str): Статус запуска (STATUS_OK или STATUS_FAIL).
        started (datetime): Момент начала запуска (Europe/Moscow).

    Returns:
        str: Тема вида "[personal-website] Бэкап: успех - backup (2026-08-30 23:01 МСК)".
    """
    stamp = started.strftime("%Y-%m-%d %H:%M")
    return f"[{PROJECT_NAME}] Бэкап: {status} - {command} ({stamp} МСК)"


def database_section_context(db: dict[str, Any]) -> dict[str, Any]:
    """Данные раздела «База данных» для шаблона отчета.

    Args:
        db (dict[str, Any]): Результат backup_db: цели, имя и объем дампа,
            срок ретеншна, число оставшихся дампов.

    Returns:
        dict[str, Any]: Словарь с целями и готовыми текстами объемов.
    """
    return {
        "targets": db["targets"],
        "dump_name": db["dump_name"],
        "size_text": format_size(db["dump_size"]),
        "retention_days": db["retention_days"],
        "remaining_text": format_count(db["remaining"]),
    }


def media_section_context(media: dict[str, Any]) -> dict[str, Any]:
    """Данные раздела «Медиа» для шаблона отчета.

    Args:
        media (dict[str, Any]): Результат backup_media: цели, число объектов
            и суммарный объем хранилища.

    Returns:
        dict[str, Any]: Словарь с целями и готовыми текстами объемов.
    """
    return {
        "targets": media["targets"],
        "count_text": format_count(media["count"]),
        "size_text": format_size(media["size"]),
    }


def render_report(context: dict[str, Any]) -> str:
    """Собрать HTML-отчет шаблоном Django.

    Args:
        context (dict[str, Any]): Данные отчета: статус, шапка запуска,
            разделы db/media, журнал при ошибке.

    Returns:
        str: HTML-документ письма.
    """
    return render_to_string(REPORT_TEMPLATE, context)


def send_report(subject: str, html: str) -> None:
    """Отправить отчет; ошибка доставки не прерывает команду.

    Пустой BACKUP_NOTIFY_EMAIL означает, что оповещения отключены.

    Args:
        subject (str): Тема письма.
        html (str): HTML-содержимое письма.
    """
    recipient = settings.BACKUP_NOTIFY_EMAIL
    if not recipient:
        return
    try:
        sent = send_mail(subject, "", settings.DEFAULT_FROM_EMAIL, [recipient], html_message=html)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Отчет о бэкапе не отправлен: %s", exc)
        return
    if not sent:
        logger.warning("Отчет о бэкапе не отправлен: почтовый backend вернул 0")


def run_with_report(command: str, label: str, operation: Callable[[], dict[str, Any]], /) -> None:
    """Выполнить операцию бэкапа и отправить отчет о результате.

    Отчеты создают только реальные запуски: ошибка операции - письмо
    со статусом ОШИБКА и журналом команды; успех с данными разделов -
    письмо со статусом успех; пропуск операции (цели не настроены) -
    без письма.

    Args:
        command (str): Имя команды для темы письма ("backup_db").
        label (str): Отображаемое имя в шапке отчета ("backup (БД и медиа)").
        operation (Callable[[], dict[str, Any]]): Выполняемая операция;
            словарь с ключами "db" и "media" и данными разделов отчета.
    """
    started = now_local()
    monotonic_start = time.monotonic()
    failure: str | None = None
    result: dict[str, Any] = {}
    capture = JournalCapture()
    with capture:
        try:
            result = operation()
        except CommandError as exc:
            failure = str(exc)
    duration = time.monotonic() - monotonic_start
    if failure:
        capture.lines.append(f"CRITICAL {failure}")
    if not failure and not any(result.values()):
        return
    status = STATUS_FAIL if failure else STATUS_OK
    context = {
        "status": status,
        "label": label,
        "hostname": socket.gethostname(),
        "started_text": f"{started.strftime('%Y-%m-%d %H:%M:%S')} МСК",
        "duration_text": format_duration(duration),
        "db": database_section_context(result["db"]) if result.get("db") else None,
        "media": media_section_context(result["media"]) if result.get("media") else None,
        "journal": "\n".join(capture.lines) if failure else None,
    }
    send_report(report_subject(command, status, started), render_report(context))
