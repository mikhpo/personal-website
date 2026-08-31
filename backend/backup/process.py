"""Запуск внешних команд системы резервного копирования.

Единая точка работы с subprocess: обертки переводят отказы команд
в CommandError с читаемым сообщением, различают вызов с захватом
вывода и с наследованием терминала, поддерживают конвейер двух
команд без временных файлов.
"""

import os
import signal
import subprocess
import sys

from django.core.management.base import CommandError


def run_command(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
    capture: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Запустить внешнюю команду и вернуть результат; отказ - CommandError.

    Args:
        command (list[str]): Команда с аргументами.
        env (dict[str, str] | None): Дополнение к текущему окружению
            (PG*-переменные для pg_dump/pg_restore, RCLONE_CONFIG_* для rclone);
            None - окружение наследуется без изменений.
        capture (bool): True - захватить вывод в result.stdout/stderr,
            False - вывод наследуется терминалом.
        check (bool): False - ненулевой код завершения не бросает исключение,
            результат возвращается как есть.

    Returns:
        subprocess.CompletedProcess[str]: Результат выполнения команды.

    Raises:
        CommandError: Команда не найдена, либо завершилась с ненулевым кодом
            (второе - только при check=True).

    Example:
        >>> result = run_command(["pg_dump", "--version"], capture=True)
        >>> result.returncode
        0
    """
    try:
        result = subprocess.run(  # noqa: S603
            command,
            env={**os.environ, **env} if env else None,
            text=True,
            capture_output=capture,
            check=False,
        )
    except FileNotFoundError as exc:
        msg = f"команда не найдена: {exc.filename}"
        raise CommandError(msg) from exc
    if result.returncode != 0:
        if capture and result.stderr:
            sys.stderr.write(result.stderr.rstrip() + "\n")
        if check:
            msg = f"команда завершилась с кодом {result.returncode}: {' '.join(command)}"
            raise CommandError(msg)
    return result


def pipe_commands(
    source: list[str],
    dest: list[str],
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Выполнить конвейер source | dest без временных файлов; отказ - CommandError.

    Вывод источника передается получателю через канал в памяти; так дамп
    цели попадает напрямую в pg_restore, не занимая диск.

    Завершение источника по SIGPIPE при успешном получателе ошибкой не
    считается: получатель вправе остановить чтение до конца потока
    (pg_restore -l читает только заголовок и оглавление дампа).

    Args:
        source (list[str]): Команда источника, пишущая поток в stdout
            (например, mc cat / rclone cat).
        dest (list[str]): Команда получателя, читающая поток из stdin
            (например, pg_restore).
        env (dict[str, str] | None): Дополнение к текущему окружению обоих
            процессов; None - окружение наследуется без изменений.

    Returns:
        subprocess.CompletedProcess[str]: Результат получателя; stdout/stderr
        захвачены.

    Raises:
        CommandError: Одна из команд не найдена, либо завершилась с ненулевым
            кодом (в сообщении указана отказавшая сторона конвейера).

    Example:
        >>> result = pipe_commands(["echo", "hello"], ["wc", "-c"])
        >>> "6" in result.stdout
        True
    """
    full_env = {**os.environ, **env} if env else None
    read_fd, write_fd = os.pipe()
    try:
        src = subprocess.Popen(  # noqa: S603
            source,
            stdout=write_fd,
            env=full_env,
        )
    except FileNotFoundError as exc:
        os.close(read_fd)
        os.close(write_fd)
        msg = f"команда не найдена: {exc.filename}"
        raise CommandError(msg) from exc
    os.close(write_fd)
    try:
        result = subprocess.run(  # noqa: S603
            dest,
            stdin=read_fd,
            env=full_env,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        src.kill()
        src.wait()
        msg = f"команда не найдена: {exc.filename}"
        raise CommandError(msg) from exc
    finally:
        os.close(read_fd)
    source_code = src.wait()
    source_sigpipe = source_code in (-signal.SIGPIPE, 128 + signal.SIGPIPE)
    if result.returncode != 0 or (source_code != 0 and not source_sigpipe):
        for stream in (result.stdout, result.stderr):
            if stream:
                sys.stderr.write(stream.rstrip() + "\n")
        failed = " ".join(dest) if source_sigpipe else " ".join(source)
        msg = f"конвейер завершился с ошибкой ({source_code}, {result.returncode}): {failed}"
        raise CommandError(msg)
    return result
