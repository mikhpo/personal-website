#!/bin/bash
#
# Скрипт для перезапуска контейнеров после изменения конфигурации.

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

# Пересоздать и запустить контейнеры в фоновом режиме.
$COMPOSE_CMD up \
    --detach \
    --force-recreate
$COMPOSE_CMD ps
