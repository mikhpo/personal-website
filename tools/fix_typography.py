#!/usr/bin/env python3
"""Поиск и автозамена запрещённых символов типографики.

Длинное тире (U+2014) заменяется на дефис, стрелка (U+2192) - на "->".
Запрещённые символы заданы байтовыми последовательностями, поэтому сам
файл скрипта правило не нарушает. Без аргументов обрабатывает все файлы,
отслеживаемые git, с аргументами - только переданные. Обрабатываются
только файлы, декодируемые как UTF-8; остальные пропускаются без
изменений. Возвращает код 1, если хотя бы в одном файле выполнена замена,
иначе - 0.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPLACEMENTS = (
    (b"\xe2\x80\x94", b"-"),
    (b"\xe2\x86\x92", b"->"),
)


def collect_files() -> list[Path]:
    """Вернуть файлы для обработки: аргументы вызова или все отслеживаемые git."""
    if len(sys.argv) > 1:
        return [Path(argument) for argument in sys.argv[1:]]

    git = shutil.which("git")
    if git is None:
        sys.stderr.write("Ошибка: git не найден, список отслеживаемых файлов получить нельзя.\n")
        sys.exit(1)

    output = subprocess.run([git, "ls-files", "-z"], check=True, capture_output=True).stdout
    return [Path(os.fsdecode(name)) for name in output.split(b"\x00") if name]


def replace_typography(path: Path) -> bool:
    """Заменить запрещённые символы в файле.

    Возвращает True при внесённой замене, False - если замен не потребовалось.
    """
    # Симлинк пропускается: перезапись записала бы вместо него обычную копию файла.
    if path.is_symlink() or not path.is_file():
        return False

    data = path.read_bytes()
    # Обрабатываются только файлы, декодируемые как UTF-8: бинарные данные
    # могут содержать те же байтовые последовательности, и замена их повредит.
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False

    if not any(old in data for old, _ in REPLACEMENTS):
        return False

    for old, new in REPLACEMENTS:
        data = data.replace(old, new)
    path.write_bytes(data)
    return True


def main() -> int:
    """Выполнить автозамену и вернуть код: 1 при внесённых заменах, 0 при их отсутствии."""
    files = collect_files()
    if not files:
        sys.stderr.write("Нет файлов для обработки.\n")
        return 0

    fixed = [path for path in files if replace_typography(path)]

    for path in fixed:
        sys.stdout.write(f"Исправлена типографика: {path}\n")

    if fixed:
        sys.stderr.write(f"Автозамена выполнена в файлах: {len(fixed)}.\n")
        sys.stderr.write("Добавьте исправленные файлы в индекс (git add) и повторите коммит.\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
