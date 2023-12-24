import logging
import os
import re
from logging import handlers
from pathlib import Path


class NoColorLogFormatter(logging.Formatter):
    """
    Бесцветное форматирование для вывода логов в файлы.
    Обесцвечивание достигается путем удаления символов соответствующей ANSI-кодировки.
    Дополнительно создается атрибут текущего времени в формате "01.01.2001".
    """

    # Регулярное выражение, соответствующее символам ANSI-кодировки.
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")

    def format(self, record):
        if self.uses_asctime() and not hasattr(record, "asctime"):
            record.asctime = self.formatTime(record, "%d.%m.%Y %H:%M:%S")
        record.msg = re.sub(self.ansi_re, "", record.msg)
        return super().format(record)

    def uses_asctime(self):
        return self._fmt.find("{asctime}") >= 0


def set_file_logger(file: str) -> logging.Logger:
    """
    Настроить отдельное журналирование для данного файла. Логирование осуществляется
        с уровнем INFO в консоль и в файлы, ротирующиеся каждый день в полночь.

    Аргументы:
        file (str): имя файла или путь файла, для которого устанавливается логирование.
            Например, это может быть атрибут __file__ модуля, вызывающего функцию.

    Возвращает:
        Объект logging.Logger.
    """
    # Определение пути сохранения логов.
    base_dir = Path(file).resolve().parent.parent.parent
    script_name = Path(file).resolve().stem
    logs_dir = os.path.join(base_dir, "logs", script_name)
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, f"{script_name}.log")

    # Общие настройки логирования.
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Добавить логирование в консоль.
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)

    # Добавить логирование в файл.
    formatter = logging.Formatter(
        fmt="[{asctime}] [{levelname}] [{filename} -> {funcName} -> {lineno}] {message}",
        datefmt="%d.%m.%Y %H:%M:%S",
        style="{",
    )
    timed_rotating_handler = handlers.TimedRotatingFileHandler(
        log_path, when="midnight", backupCount=7
    )
    timed_rotating_handler.setFormatter(formatter)
    logger.addHandler(timed_rotating_handler)

    # Функция возвращает объект Logger.
    return logger
