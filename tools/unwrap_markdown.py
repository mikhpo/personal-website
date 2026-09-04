#!/usr/bin/env python3
"""Развертывание жестких переносов строк в Markdown-файлах.

Абзац и пункт списка приводятся к одной строке: строки, которые Markdown
рендерит как единый блок, объединяются через одинарный пробел. Код-блоки,
таблицы, заголовки, цитаты, HTML-блоки, тематические разделители и
frontmatter не изменяются. Без аргументов обрабатывает все отслеживаемые
git markdown-файлы, с аргументами - только переданные. Возвращает код 1,
если хотя бы в одном файле развернуты переносы, иначе - 0.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MARKDOWN_EXTENSIONS = (".md", ".markdown")

FENCE = re.compile(r"^ *(```+|~~~+)")
LIST_ITEM = re.compile(r"^ *(?:[-*+]|\d+[.)])\s+\S")
SINGLE_LINE_BLOCK = re.compile(r"^ {0,3}(?:-{3,}|\*{3,}|_{3,}|=+)\s*$")
INDENTED_CODE_INDENT = 4


def collect_files() -> list[Path]:
    """Вернуть markdown-файлы для обработки: аргументы вызова или все отслеживаемые git."""
    if len(sys.argv) > 1:
        candidates = [Path(argument) for argument in sys.argv[1:]]
    else:
        git = shutil.which("git")
        if git is None:
            sys.stderr.write("Ошибка: git не найден, список отслеживаемых файлов получить нельзя.\n")
            sys.exit(1)
        output = subprocess.run([git, "ls-files", "-z"], check=True, capture_output=True).stdout
        candidates = [Path(os.fsdecode(name)) for name in output.split(b"\x00") if name]
    return [path for path in candidates if path.suffix.lower() in MARKDOWN_EXTENSIONS]


def split_frontmatter(lines: list[str]) -> tuple[list[str], list[str]]:
    """Разделить строки на frontmatter и остальное содержимое.

    Frontmatter - начальный блок между разделителями --- и --- (или ...).
    Без закрывающего разделителя весь файл считается frontmatter.
    Возвращает пару (служебные строки, обрабатываемые строки).
    """
    if not lines or lines[0].strip() != "---":
        return [], list(lines)
    closing = next((i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")), None)
    if closing is None:
        return list(lines), []
    return lines[: closing + 1], lines[closing + 1 :]


def is_block_start(stripped: str) -> bool:
    """Определить, начинает ли строка однострочный блок, не объединяемый с соседями."""
    return stripped.startswith(("#", ">", "|", "<")) or SINGLE_LINE_BLOCK.match(stripped) is not None


def starts_indented_code(line: str, buffer: list[str]) -> bool:
    """Определить отступный код-блок: строка с отступом от 4 пробелов вне накопленного блока."""
    return not buffer and len(line) - len(line.lstrip(" ")) >= INDENTED_CODE_INDENT


def is_hard_break(buffer: list[str]) -> bool:
    """Определить жесткий перенос: обратный слэш в конце накопленной строки."""
    return bool(buffer) and buffer[-1].endswith("\\")


def flush_block(result: list[str], buffer: list[str]) -> None:
    """Добавить накопленный блок в результат одной строкой."""
    if buffer:
        result.append(" ".join(buffer))
        buffer.clear()


def unwrap_lines(lines: list[str]) -> list[str]:
    """Развернуть мягкие переносы в списке строк и вернуть новый список.

    Соседние строки одного блока (абзац, пункт списка с продолжениями)
    объединяются в одну строку. Frontmatter, фенсы кода и строки внутри
    них копируются без изменений.
    """
    result: list[str] = []
    buffer: list[str] = []
    verbatim, rest = split_frontmatter(lines)
    result.extend(verbatim)
    in_code_fence = False
    for line in rest:
        stripped = line.strip()
        if FENCE.match(line):
            flush_block(result, buffer)
            result.append(line)
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            result.append(line)
            continue
        if not stripped:
            flush_block(result, buffer)
            result.append(line)
            continue
        if is_block_start(stripped):
            flush_block(result, buffer)
            result.append(line)
            continue
        if LIST_ITEM.match(line):
            flush_block(result, buffer)
            buffer.append(line.rstrip())
            continue
        if starts_indented_code(line, buffer):
            result.append(line.rstrip())
            continue
        if is_hard_break(buffer):
            flush_block(result, buffer)
        buffer.append(line.rstrip() if not buffer else stripped)
    flush_block(result, buffer)
    return result


def unwrap_markdown(path: Path) -> bool:
    """Развернуть переносы в файле.

    Возвращает True при внесенном изменении, False - если файл не изменен.
    """
    # Симлинк пропускается: перезапись записала бы вместо него обычную копию файла.
    if path.is_symlink() or not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    updated_text = "\n".join(unwrap_lines(text.splitlines()))
    if text.endswith("\n"):
        updated_text += "\n"
    if updated_text == text:
        return False
    path.write_text(updated_text, encoding="utf-8")
    return True


def main() -> int:
    """Выполнить развертывание переносов и вернуть код: 1 при изменениях, 0 при их отсутствии."""
    files = collect_files()
    if not files:
        sys.stderr.write("Нет файлов для обработки.\n")
        return 0

    changed = [path for path in files if unwrap_markdown(path)]

    for path in changed:
        sys.stdout.write(f"Развернуты переносы: {path}\n")

    if changed:
        sys.stderr.write(f"Переносы развернуты в файлах: {len(changed)}.\n")
        sys.stderr.write("Добавьте исправленные файлы в индекс (git add) и повторите коммит.\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
