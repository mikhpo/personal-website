#!/usr/bin/env python3
"""Синхронизация ветки и тегов между зеркалами репозитория (GitHub и SourceCraft).

Скрипт сравнивает состояния ветки и тегов всех зеркал списка PEERS и доставляет
отстающим только fast-forward push. Неосновные ветки синхронизируются ручными
прогонами, в CI скрипт вызывается без имени ветки (только main).

Состояния зеркал временно загружаются в служебные ссылки refs/sync внутри текущего
репозитория и удаляются при завершении работы. Временные файлы и каталоги не создаются.
При расхождении ветки или конфликте тегов скрипт печатает диагностику и завершается
с кодом 1, ничего не меняя. Ошибка вызова, git или сети завершает скрипт с кодом 2.
Полная синхронность или выполненная доставка дают код 0. Аутентификация (SSH)
настраивается в окружении вызова.

Переменная окружения не требуется: платформа CI сообщается штатными переменными
(GITHUB_ACTIONS у GitHub, SOURCECRAFT_CI у SourceCraft), и состояние своего зеркала
берется из текущего репозитория без обращения по SSH - ключ для доступа к зеркалу
самому себе не нужен. При локальном запуске ни одна из переменных не задана и оба
зеркала опрашиваются по SSH.

Примеры вызова:

    tools/sync_mirrors.py              # синхронизировать main и теги
    tools/sync_mirrors.py dev          # синхронизировать ветку dev и теги
    tools/sync_mirrors.py -h           # справка по вызову
"""

import argparse
import os
import shutil
import subprocess
import sys
from typing import NoReturn

# Зеркала как пары «метка - URL»; добавление платформы - новая запись в списке.
PEERS: list[tuple[str, str]] = [
    ("github", "git@github.com:mikhpo/personal-website.git"),
    ("sourcraft", "ssh://ssh.sourcecraft.dev/mikhpo/personal-website.git"),
]

EXIT_OK = 0
EXIT_DIVERGED = 1
EXIT_ERROR = 2

# Минимальное число сегментов ссылки тега: refs/sync/<зеркало>/tags/<тег>.
MIN_TAG_REF_PARTS = 5


def detect_ci_mirror() -> str | None:
    """Вернуть метку платформы, в CI которой выполняется скрипт, или None при локальном запуске.

    Платформы сообщают о себе штатными переменными окружения, поэтому отдельной
    настройки обертки не требуется. Локальный запуск не задает ни одну из них.
    """
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return "github"
    if os.environ.get("SOURCECRAFT_CI"):
        return "sourcraft"
    return None


def build_parser() -> argparse.ArgumentParser:
    """Собрать парсер аргументов: опциональное имя ветки и штатная справка -h/--help."""
    parser = argparse.ArgumentParser(
        prog="tools/sync_mirrors.py",
        description="Синхронизация ветки и тегов между зеркалами репозитория.",
        add_help=True,
    )
    parser.add_argument("branch", nargs="?", default="main", help="имя ветки (по умолчанию main)")
    return parser


def log(message: str) -> None:
    """Напечатать сообщение прогресса."""
    sys.stdout.write(f"{message}\n")


def exit_with_error(message: str) -> NoReturn:
    """Сообщить об ошибке git или сети и завершить скрипт с кодом 2."""
    sys.stderr.write(f"Ошибка: {message}\n")
    sys.exit(EXIT_ERROR)


def require_git_binary() -> str:
    """Вернуть путь до исполняемого git. Отсутствие утилиты завершает скрипт с кодом 2."""
    git = shutil.which("git")
    if git is None:
        exit_with_error("git не найден в PATH")
    return git


def try_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Выполнить команду git и вернуть результат независимо от кода возврата."""
    return subprocess.run([require_git_binary(), *args], capture_output=True, text=True, check=False)


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Выполнить команду git в текущем репозитории. Падение команды завершает скрипт с кодом 2."""
    result = try_git(*args)
    if result.returncode != 0:
        exit_with_error(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result


def cleanup_sync_refs() -> None:
    """Удалить служебные ссылки refs/sync из текущего репозитория.

    Эти ссылки временно хранят загруженные состояния зеркал. Очистка выполняется
    при любом завершении скрипта, в том числе после ошибок, и обязана быть
    терпимой к неудаче: неудачное удаление не должно завершать скрипт с ошибкой.
    """
    refs = run_git("for-each-ref", "--format=%(refname)", "refs/sync").stdout.splitlines()
    for ref in refs:
        deleted = try_git("update-ref", "-d", ref)
        if deleted.returncode != 0:
            log(f"Не удалось удалить служебный ref {ref} при очистке: {deleted.stderr.strip()}")


def fetch_peer(name: str, url: str, branch: str) -> None:
    """Получить ветку и теги зеркала в служебные ссылки текущего репозитория.

    Состояние зеркала из SYNC_SELF копируется из текущего репозитория без
    обращения по SSH: CI-обертка выполняется в копии этого зеркала.

    Ветка может существовать не на всех зеркалах, а загрузка отсутствующей ветки
    завершается ошибкой целиком, вместе с тегами. Поэтому наличие ветки проверяется
    отдельным запросом списка веток зеркала, и у зеркала без ветки получаются только теги.
    """
    if name == detect_ci_mirror():
        fetch_local_state(name, branch)
        return
    listing = run_git("ls-remote", "--heads", url, f"refs/heads/{branch}")
    has_branch = bool(listing.stdout.split())
    if has_branch:
        log(f"Получение ветки {branch} и тегов зеркала {name}...")
        refspecs = [f"+refs/heads/{branch}:refs/sync/{name}/{branch}"]
    else:
        log(f"Ветки {branch} нет на зеркале {name}; получение тегов.")
        refspecs = []
    run_git("fetch", "--no-tags", "--quiet", url, *refspecs, f"+refs/tags/*:refs/sync/{name}/tags/*")


def fetch_local_state(name: str, branch: str) -> None:
    """Скопировать состояние ветки и тегов текущего репозитория в служебные ссылки зеркала name.

    Ветка берется по имени, а при его отсутствии - HEAD: рабочая копия CI-обертки
    выполняет checkout и detached-состояние, и ветку. Отсутствие локальных тегов
    означает отсутствие тегов на зеркале; отдельной проверки подлинности не требуется.
    """
    sha = resolve_sha(f"refs/heads/{branch}") or resolve_sha("HEAD")
    if sha is not None:
        log(f"Зеркало {name} - текущий репозиторий; ветка {branch}: {sha[:12]}.")
        run_git("update-ref", f"refs/sync/{name}/{branch}", sha)
    else:
        log(f"Ветки {branch} нет в текущем репозитории (зеркало {name}).")
    listing = run_git("for-each-ref", "--format=%(objectname) %(refname)", "refs/tags")
    for line in listing.stdout.splitlines():
        sha, refname = line.split(" ")
        run_git("update-ref", f"refs/sync/{name}/tags/{refname.removeprefix('refs/tags/')}", sha)


def resolve_sha(ref: str) -> str | None:
    """Вернуть SHA ссылки текущего репозитория или None, если ссылки нет. Ошибка git завершает скрипт с кодом 2."""
    result = try_git("rev-parse", "--verify", "--quiet", ref)
    if result.returncode == 0:
        return result.stdout.strip()
    if result.returncode == 1:
        return None
    exit_with_error(f"git rev-parse --verify {ref}: {result.stderr.strip()}")


def is_ancestor(older: str, younger: str) -> bool:
    """Проверить, что первое из состояний предшествует второму, то есть вся история первого входит в историю второго.

    Ошибка git завершает скрипт с кодом 2.
    """
    result = try_git("merge-base", "--is-ancestor", older, younger)
    if result.returncode > 1:
        exit_with_error(f"git merge-base --is-ancestor {older} {younger}: {result.stderr.strip()}")
    return result.returncode == 0


def find_leading_mirror(shas: dict[str, str]) -> str | None:
    """Вернуть метку зеркала, состояние которого содержит состояния всех остальных, или None."""
    for candidate, candidate_sha in shas.items():
        others = (sha for name, sha in shas.items() if name != candidate)
        if all(is_ancestor(other, candidate_sha) for other in others):
            return candidate
    return None


def fail_branch_divergence(branch: str, shas: dict[str, str]) -> NoReturn:
    """Напечатать диагностику расхождения ветки и завершить скрипт с кодом 1."""
    log(f"Расхождение ветки {branch} между зеркалами; синхронизация не выполнена:")
    for name, sha in shas.items():
        log(f"  {name} - {sha}")
    log(
        "Расхождение разрешается локально: git merge-base <sha1> <sha2>, merge одной стороны в другую, "
        "затем повторный запуск.",
    )
    sys.exit(EXIT_DIVERGED)


def sync_branch(branch: str) -> None:
    """Синхронизировать ветку между зеркалами.

    Находится состояние ветки, в истории которого содержатся состояния всех остальных
    зеркал, и доставляется зеркалам, которые отстают или вовсе не имеют ветки.
    Отсутствие ветки на зеркале - крайний случай отставания: ветка доставляется
    созданием, без force, удаления не выполняются. Если ветки нет ни на одном зеркале,
    синхронизация ветки пропускается.
    """
    shas: dict[str, str] = {}
    for name, _ in PEERS:
        sha = resolve_sha(f"refs/sync/{name}/{branch}")
        if sha is not None:
            shas[name] = sha
    if not shas:
        log(f"Ветки {branch} нет ни на одном зеркале; синхронизация ветки пропущена.")
        return
    tip = find_leading_mirror(shas)
    if tip is None:
        fail_branch_divergence(branch, shas)
    tip_sha = shas[tip]
    pushed = False
    for name, url in PEERS:
        if shas.get(name) == tip_sha:
            continue
        if name in shas:
            log(f"Зеркало {name} отстает по ветке {branch}; отправка {tip_sha}...")
        else:
            log(f"Ветки {branch} нет на зеркале {name}; отправка...")
        run_git("push", "--quiet", url, f"{tip_sha}:refs/heads/{branch}")
        pushed = True
    if pushed:
        log(f"Ветка {branch} синхронизирована fast-forward push-ем.")
    else:
        log(f"Ветка {branch} у всех зеркал совпадает.")


def fail_tag_conflict(tag: str, states: dict[str, str]) -> NoReturn:
    """Напечатать диагностику конфликта тега и завершить скрипт с кодом 1."""
    log(f"Конфликт тега {tag}: разные состояния на зеркалах; синхронизация не выполнена:")
    for name, sha in states.items():
        log(f"  {name} - {sha}")
    log("Тег вручную приводится к одному состоянию, затем запускается повторная синхронизация.")
    sys.exit(EXIT_DIVERGED)


def collect_tag_states() -> dict[str, dict[str, str]]:
    """Вернуть состояния тегов: имя тега -> метка зеркала -> SHA."""
    result = run_git("for-each-ref", "--format=%(refname) %(objectname)", "refs/sync")
    states: dict[str, dict[str, str]] = {}
    for line in result.stdout.splitlines():
        refname, sha = line.split(" ")
        parts = refname.split("/")
        if len(parts) < MIN_TAG_REF_PARTS or parts[3] != "tags":
            continue
        states.setdefault("/".join(parts[4:]), {})[parts[2]] = sha
    return states


def sync_tags() -> None:
    """Синхронизировать теги: доставить недостающие зеркалам. Разные состояния одного тега на зеркалах - конфликт."""
    states_by_tag = collect_tag_states()
    pushed = False
    for tag in sorted(states_by_tag):
        states = states_by_tag[tag]
        if len(set(states.values())) > 1:
            fail_tag_conflict(tag, states)
        source = next(name for name, _ in PEERS if name in states)
        for name, url in PEERS:
            if name in states:
                continue
            log(f"Тег {tag} отсутствует на зеркале {name}; отправка...")
            run_git("push", "--quiet", url, f"refs/sync/{source}/tags/{tag}:refs/tags/{tag}")
            pushed = True
    log("Теги синхронизированы." if pushed else "Теги у всех зеркал совпадают.")


def main() -> int:
    """Выполнить синхронизацию зеркал и вернуть код завершения."""
    parser = build_parser()
    args = parser.parse_args()
    branch = args.branch
    try:
        names = ", ".join(name for name, _ in PEERS)
        log(f"Синхронизация ветки {branch} и тегов зеркал: {names}")
        for name, url in PEERS:
            fetch_peer(name, url, branch)
        sync_branch(branch)
        sync_tags()
    finally:
        cleanup_sync_refs()
    log("Синхронизация завершена.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
