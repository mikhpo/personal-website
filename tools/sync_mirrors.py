#!/usr/bin/env python3
"""Синхронизация ветки и тегов между зеркалами репозитория (GitHub и SourceCraft).

Скрипт сравнивает состояния ветки и тегов всех зеркал списка PEERS и доставляет
отстающим только fast-forward push. Неосновные ветки синхронизируются ручными
прогонами; в CI скрипт вызывается без имени ветки (только main). Состояния
получаются fetch-ем в служебные namespaced-рефы refs/sync/ текущего репозитория
и удаляются при завершении; временные файлы и каталоги не создаются. При
расхождении ветки или конфликте тегов завершается с кодом 1 и диагностикой,
ничего не меняя; ошибка вызова, git или сети - код 2; полная синхронность или
выполненная доставка - код 0. Аутентификация (SSH) настраивается в окружении вызова.

Примеры вызова:

    tools/sync_mirrors.py              # синхронизировать main и теги
    tools/sync_mirrors.py dev          # синхронизировать ветку dev и теги
    tools/sync_mirrors.py -h           # справка по вызову
"""

import argparse
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


def fail_operational(message: str) -> NoReturn:
    """Сообщить об ошибке git или сети и завершить скрипт с кодом 2."""
    sys.stderr.write(f"Ошибка: {message}\n")
    sys.exit(EXIT_ERROR)


def git_binary() -> str:
    """Вернуть путь до исполняемого git; отсутствие утилиты завершает скрипт с кодом 2."""
    git = shutil.which("git")
    if git is None:
        fail_operational("git не найден в PATH")
    return git


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Выполнить git в текущем репозитории; падение команды завершает скрипт с кодом 2."""
    result = subprocess.run([git_binary(), *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        fail_operational(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result


def cleanup_sync_refs() -> None:
    """Удалить служебные refs/sync/* текущего репозитория; выполняется при любом завершении."""
    refs = run_git("for-each-ref", "--format=%(refname)", "refs/sync").stdout.splitlines()
    for ref in refs:
        deleted = subprocess.run(
            [git_binary(), "update-ref", "-d", ref],
            capture_output=True,
            text=True,
            check=False,
        )
        if deleted.returncode != 0:
            log(f"Не удалось удалить служебный ref {ref} при очистке: {deleted.stderr.strip()}")


def fetch_peer(name: str, url: str, branch: str) -> None:
    """Получить ветку и теги зеркала в namespaced-рефы текущего репозитория.

    Ветка может существовать не на всех зеркалах, а fetch по refspec отсутствующей
    ветки падает целиком, поэтому наличие проверяется ls-remote; у зеркала без ветки
    получаются только теги.
    """
    listing = run_git("ls-remote", "--heads", url, f"refs/heads/{branch}")
    has_branch = bool(listing.stdout.split())
    if has_branch:
        log(f"Получение ветки {branch} и тегов зеркала {name}...")
        refspecs = [f"+refs/heads/{branch}:refs/sync/{name}/{branch}"]
    else:
        log(f"Ветки {branch} нет на зеркале {name}; получение тегов.")
        refspecs = []
    run_git("fetch", "--no-tags", "--quiet", url, *refspecs, f"+refs/tags/*:refs/sync/{name}/tags/*")


def ref_sha(ref: str) -> str | None:
    """Вернуть SHA рефа текущего репозитория или None, если рефа нет; ошибка git завершает скрипт."""
    result = subprocess.run(
        [git_binary(), "rev-parse", "--verify", "--quiet", ref],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    if result.returncode == 1:
        return None
    fail_operational(f"git rev-parse --verify {ref}: {result.stderr.strip()}")


def is_ancestor(older: str, younger: str) -> bool:
    """Проверить, является ли состояние older предком younger; ошибка git завершает скрипт."""
    result = subprocess.run(
        [git_binary(), "merge-base", "--is-ancestor", older, younger],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode > 1:
        fail_operational(f"git merge-base --is-ancestor {older} {younger}: {result.stderr.strip()}")
    return result.returncode == 0


def find_tip(shas: dict[str, str]) -> str | None:
    """Вернуть метку зеркала, состояние которого является потомком всех остальных, или None."""
    for candidate, candidate_sha in shas.items():
        others = (sha for name, sha in shas.items() if name != candidate)
        if all(is_ancestor(other, candidate_sha) for other in others):
            return candidate
    return None


def fail_main_divergence(branch: str, shas: dict[str, str]) -> NoReturn:
    """Напечатать диагностику расхождения ветки и завершить скрипт с кодом 1."""
    log(f"Расхождение ветки {branch} между зеркалами; синхронизация не выполнена:")
    for name, sha in shas.items():
        log(f"  {name} - {sha}")
    log(
        "Расхождение разрешается локально: git merge-base <sha1> <sha2>, merge одной стороны в другую, "
        "затем повторный запуск.",
    )
    sys.exit(EXIT_DIVERGED)


def sync_main(branch: str) -> None:
    """Синхронизировать ветку: доставить отстающим и не имеющим ее зеркалам вершину, потомка остальных.

    Отсутствие ветки на зеркале - крайний случай отставания: ветка доставляется созданием
    (без force, удалений нет). Если ветки нет ни на одном зеркале, синхронизация ветки
    пропускается.
    """
    shas: dict[str, str] = {}
    for name, _ in PEERS:
        sha = ref_sha(f"refs/sync/{name}/{branch}")
        if sha is not None:
            shas[name] = sha
    if not shas:
        log(f"Ветки {branch} нет ни на одном зеркале; синхронизация ветки пропущена.")
        return
    tip = find_tip(shas)
    if tip is None:
        fail_main_divergence(branch, shas)
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
    log("Тег приводится к одному состоянию вручную на обеих платформах, затем запускается повторная синхронизация.")
    sys.exit(EXIT_DIVERGED)


def collect_tag_states() -> dict[str, dict[str, str]]:
    """Вернуть состояния тегов: имя тега -> метка зеркала -> SHA."""
    result = run_git("for-each-ref", "--format=%(refname) %(objectname)", "refs/sync")
    states: dict[str, dict[str, str]] = {}
    for line in result.stdout.splitlines():
        refname, sha = line.split(" ")
        parts = refname.split("/")
        if parts[3] != "tags":
            continue
        states.setdefault("/".join(parts[4:]), {})[parts[2]] = sha
    return states


def sync_tags() -> None:
    """Синхронизировать теги: доставить отсутствующим зеркалам; разные состояния одного тега - конфликт."""
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
        sync_main(branch)
        sync_tags()
    finally:
        cleanup_sync_refs()
    log("Синхронизация завершена.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
