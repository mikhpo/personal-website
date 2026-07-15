#!/bin/bash
#
# Скрипт для перезапуска контейнеров после изменения кода проекта.

# Выйти в случае ошибки.
set -e

#######################################
# Определить доступную команду Docker Compose.
# Приоритет отдается плагину V2 (`docker compose`),
# в случае его отсутствия используется V1 (`docker-compose`).
# Возвращает строку с командой через stdout.
#######################################
function detect_compose_cmd() {
    if docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
        echo "docker-compose"
    else
        echo "Ошибка: Docker Compose не найден. Установите плагин docker-compose-plugin или Docker Compose V1." >&2
        exit 1
    fi
}

COMPOSE_CMD="$(detect_compose_cmd)"
readonly COMPOSE_CMD

project_root="$(dirname "$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")")"
cd "$project_root" || exit

# Создать резервную копию базы данных и загруженных файлов.
bash "$project_root"/personal_website/scripts/pgbackup.sh
bash "$project_root"/personal_website/scripts/pgrestore.sh

# Вытянуть изменения основной ветки
git fetch origin
git checkout main
git pull

# Вытянуть новую версию образа, пересоздать контейнеры,
# запустить контейнеры в фоновом режиме, удалить
# неиспользуемые контейнеры и образы.
$COMPOSE_CMD pull
$COMPOSE_CMD up \
    --detach \
    --force-recreate \
    --remove-orphans
$COMPOSE_CMD ps
docker image prune
