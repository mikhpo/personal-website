#!/usr/bin/env python3
"""Синхронизация main и тегов между зеркалами репозитория (GitHub и SourceCraft).

Скрипт сравнивает состояния main и тегов всех зеркал списка PEERS и доставляет
отстающим только fast-forward push. Состояния получаются fetch-ем в служебные
namespaced-рефы refs/sync/ текущего репозитория и удаляются при завершении;
временные файлы и каталоги не создаются. При расхождении main или конфликте тегов
завершается с кодом 1 и диагностикой, ничего не меняя; ошибка git или сети - код 2;
полная синхронность или выполненная доставка - код 0. Аргументов и флагов нет;
аутентификация (SSH) настраивается в окружении вызова.
"""

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


def log(message: str) -> None:
    """Напечатать сообщение прогресса."""
    sys.stdout.write(f"{message}\n")


def fail_operational(message: str) -> NoReturn:
    """Сообщить об операционной ошибке git или сети и завершить скрипт с кодом 2."""
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


def fetch_peer(name: str, url: str) -> None:
    """Получить main и теги зеркала в namespaced-рефы текущего репозитория."""
    log(f"Получение main и тегов зеркала {name}...")
    run_git(
        "fetch",
        "--no-tags",
        "--quiet",
        url,
        f"+refs/heads/main:refs/sync/{name}/main",
        f"+refs/tags/*:refs/sync/{name}/tags/*",
    )


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


def fail_main_divergence(shas: dict[str, str]) -> NoReturn:
    """Напечатать диагностику расхождения main и завершить скрипт с кодом 1."""
    log("Расхождение main между зеркалами; синхронизация не выполнена:")
    for name, sha in shas.items():
        log(f"  {name} - {sha}")
    log(
        "Расхождение разрешается локально: git merge-base <sha1> <sha2>, merge одной стороны в другую, "
        "затем повторный запуск.",
    )
    sys.exit(EXIT_DIVERGED)


def sync_main() -> None:
    """Синхронизировать main: доставить отстающим зеркалам вершину, потомка всех остальных состояний."""
    shas = {}
    for name, _ in PEERS:
        result = run_git("rev-parse", "--verify", f"refs/sync/{name}/main")
        shas[name] = result.stdout.strip()
    tip = find_tip(shas)
    if tip is None:
        fail_main_divergence(shas)
    tip_sha = shas[tip]
    pushed = False
    for name, url in PEERS:
        if name == tip or shas[name] == tip_sha:
            continue
        log(f"Зеркало {name} отстает по main; отправка {tip_sha}...")
        run_git("push", "--quiet", url, f"{tip_sha}:refs/heads/main")
        pushed = True
    log("main синхронизирован fast-forward push-ем." if pushed else "main у всех зеркал совпадает.")


def fail_tag_conflict(tag: str, states: dict[str, str]) -> NoReturn:
    """Напечатать диагностику конфликта тега и завершить скрипт с кодом 1."""
    log(f"Конфликт тега {tag}: разные состояния на зеркалах; синхронизация не выполнена:")
    for name, sha in states.items():
        log(f"  {name} - {sha}")
    log("Тег приводится к одному состоянию вручную на обеих платформах, затем запускается повторная синхронизация.")
    sys.exit(EXIT_DIVERGED)


def collect_tag_states() -> dict[str, dict[str, str]]:
    """Вернуть состояния тегов: имя тега -> метка зеркала -> SHA."""
    result = run_git("for-each-ref", "--format=%(refname) %(objectname)", "refs/sync/*/tags/*")
    states: dict[str, dict[str, str]] = {}
    for line in result.stdout.splitlines():
        refname, sha = line.split(" ")
        parts = refname.split("/")
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
    try:
        names = ", ".join(name for name, _ in PEERS)
        log(f"Синхронизация main и тегов зеркал: {names}")
        for name, url in PEERS:
            fetch_peer(name, url)
        sync_main()
        sync_tags()
    finally:
        cleanup_sync_refs()
    log("Синхронизация завершена.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
