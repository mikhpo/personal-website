#!/bin/bash
#
# Синхронизировать main и теги между зеркалами репозитория (GitHub и SourceCraft).
#
# Скрипт сравнивает состояния main и тегов всех зеркал списка PEERS и доставляет
# отстающим только fast-forward push. Состояния получаются fetch-ем в служебные
# namespaced-рефы refs/sync/ текущего репозитория и удаляются при завершении;
# временные файлы и каталоги не создаются. При расхождении main или конфликте тегов
# завершается с кодом 1 и диагностикой, ничего не меняя; ошибка git или сети - код 2;
# полная синхронность или выполненная доставка - код 0. Аргументов и флагов нет;
# аутентификация (SSH) настраивается в окружении вызова.

set -euo pipefail

# Зеркала как пары «метка|URL»; добавление платформы - новая запись в списке.
PEERS=(
    "github|git@github.com:mikhpo/personal-website.git"
    "sourcraft|ssh://ssh.sourcecraft.dev/mikhpo/personal-website.git"
)

log() {
    printf '%s\n' "$*"
}

# Завершить скрипт: $1 - код выхода (1 - расхождение, 2 - ошибка git/сети), $2 - сообщение.
die() {
    printf 'Ошибка: %s\n' "$2" >&2
    exit "$1"
}

# Выполнить git в текущем репозитории; падение команды - операционная ошибка с кодом 2.
run_git() {
    if ! git "$@"; then
        die 2 "команда git $* завершилась с ошибкой"
    fi
}

# Удалить служебные refs/sync/* текущего репозитория; выполняется при любом завершении.
cleanup_refs() {
    local ref
    while IFS= read -r ref; do
        if [ -z "$ref" ]; then
            continue
        fi
        if ! git update-ref -d "$ref" 2>/dev/null; then
            log "Не удалось удалить служебный ref $ref при очистке."
        fi
    done < <(git for-each-ref --format='%(refname)' refs/sync)
}
trap cleanup_refs EXIT

# Получить main и теги зеркала в namespaced-рефы текущего репозитория.
fetch_peer() {
    local name=$1 url=$2
    log "Получение main и тегов зеркала $name..."
    run_git fetch --no-tags --quiet "$url" \
        "+refs/heads/main:refs/sync/$name/main" \
        "+refs/tags/*:refs/sync/$name/tags/*"
}

# Синхронизировать main: доставить отстающим зеркалам вершину, потомка всех остальных состояний.
sync_main() {
    local -a names=() urls=() shas=()
    local entry name url sha tip="" tip_sha="" found rc i j pushed=0
    for entry in "${PEERS[@]}"; do
        IFS='|' read -r name url <<< "$entry"
        if ! sha=$(git rev-parse --verify "refs/sync/$name/main"); then
            die 2 "не получено состояние main зеркала $name"
        fi
        names+=("$name")
        urls+=("$url")
        shas+=("$sha")
    done
    for i in "${!names[@]}"; do
        found=1
        for j in "${!names[@]}"; do
            if [ "$i" = "$j" ]; then
                continue
            fi
            rc=0
            git merge-base --is-ancestor "${shas[j]}" "${shas[i]}" || rc=$?
            if [ "$rc" -gt 1 ]; then
                die 2 "сравнение состояний main зеркал ${names[j]} и ${names[i]} завершилось с ошибкой"
            fi
            if [ "$rc" -eq 1 ]; then
                found=0
                break
            fi
        done
        if [ "$found" -eq 1 ]; then
            tip=${names[i]}
            tip_sha=${shas[i]}
            break
        fi
    done
    if [ -z "$tip" ]; then
        log "Расхождение main между зеркалами; синхронизация не выполнена:"
        for i in "${!names[@]}"; do
            log "  ${names[i]} - ${shas[i]}"
        done
        log "Расхождение разрешается локально: git merge-base <sha1> <sha2>, merge одной стороны в другую, затем повторный запуск."
        exit 1
    fi
    for i in "${!names[@]}"; do
        if [ "${names[i]}" = "$tip" ] || [ "${shas[i]}" = "$tip_sha" ]; then
            continue
        fi
        log "Зеркало ${names[i]} отстает по main; отправка ${tip_sha}..."
        run_git push --quiet "${urls[i]}" "${tip_sha}:refs/heads/main"
        pushed=1
    done
    if [ "$pushed" -eq 1 ]; then
        log "main синхронизирован fast-forward push-ем."
    else
        log "main у всех зеркал совпадает."
    fi
}

# Синхронизировать теги: доставить отсутствующим зеркалам; разные состояния одного тега - конфликт.
sync_tags() {
    local norm tag lines count src entry name url pushed=0
    norm=$(git for-each-ref --format='%(refname) %(objectname)' 'refs/sync/*/tags/*' \
        | awk '{ n=split($1, p, "/"); t=""; for (k=5; k<=n; k++) t=t (k>5 ? "/" : "") p[k]; print p[3], t, $2 }')
    while IFS= read -r tag; do
        if [ -z "$tag" ]; then
            continue
        fi
        lines=$(printf '%s\n' "$norm" | awk -v t="$tag" '$2 == t {print $1, $3}')
        count=$(printf '%s\n' "$lines" | awk '{print $2}' | sort -u | awk 'END {print NR}')
        if [ "$count" -gt 1 ]; then
            log "Конфликт тега $tag: разные состояния на зеркалах; синхронизация не выполнена:"
            printf '%s\n' "$lines" | while IFS=' ' read -r p s; do log "  $p - $s"; done
            log "Тег приводится к одному состоянию вручную на обеих платформах, затем запускается повторная синхронизация."
            exit 1
        fi
        src=$(printf '%s\n' "$lines" | awk '{print $1; exit}')
        for entry in "${PEERS[@]}"; do
            IFS='|' read -r name url <<< "$entry"
            if printf '%s\n' "$lines" | awk -v n="$name" '$1 == n {found=1} END {exit !found}'; then
                continue
            fi
            log "Тег $tag отсутствует на зеркале $name; отправка..."
            run_git push --quiet "$url" "refs/sync/$src/tags/$tag:refs/tags/$tag"
            pushed=1
        done
    done < <(printf '%s\n' "$norm" | awk 'NF {print $2}' | sort -u)
    if [ "$pushed" -eq 1 ]; then
        log "Теги синхронизированы."
    else
        log "Теги у всех зеркал совпадают."
    fi
}

names_list=$(printf '%s, ' "${PEERS[@]%%|*}")
log "Синхронизация main и тегов зеркал: ${names_list%, }"
for entry in "${PEERS[@]}"; do
    IFS='|' read -r name url <<< "$entry"
    fetch_peer "$name" "$url"
done
sync_main
sync_tags
log "Синхронизация завершена."
