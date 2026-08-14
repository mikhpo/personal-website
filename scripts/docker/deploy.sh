#!/bin/bash
#
# Скрипт для развертывания обновления через Docker.
# Выполняется на сервере (в том числе из CI/CD): обновляет файлы проекта,
# подготавливает каталоги и пересоздает контейнеры из свежих образов.

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

# Определение рабочих файлов проекта.
project_root="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
readonly dotenv="$project_root/.env"
cd "$project_root" || exit

#######################################
# Загрузить переменные окружения из .env файла
# или выйти, если файл не существует.
#######################################
function load_dotenv() {
    if [ -f "$dotenv" ]; then
        set -a
        # shellcheck disable=SC1090
        . "$dotenv"
        set +a
        echo "Переменные окружения загружены из файла $dotenv"
    else
        echo "Файл с переменными окружения $dotenv не существует"
        exit 1
    fi
}

#######################################
# Скачать SSL-сертификат PostgreSQL (идемпотентно).
# Сертификат монтируется в контейнер website read-only,
# поэтому должен присутствовать на хосте до запуска контейнеров.
#######################################
function load_postgres_cert() {
    bash "$project_root/scripts/pgcert.sh"
}

#######################################
# Обновить файлы проекта из основной ветки репозитория.
# Необходимо для получения актуальных версий compose.yaml и скриптов.
#######################################
function pull_repository() {
    git fetch origin
    git checkout main
    git pull
}

#######################################
# Создать каталоги хоста для bind-mounts Docker Compose.
# Каталоги создаются заранее с корректными правами,
# иначе Docker создает их от имени пользователя root.
#######################################
function create_docker_directories() {
    echo "Создание директорий для Docker volumes..."
    mkdir -p "$project_root/storage"
    mkdir -p "$project_root/static"
    mkdir -p "$project_root/backups"
    mkdir -p "$project_root/logs"
    mkdir -p "$project_root/temp"
    mkdir -p "$project_root/traefik/letsencrypt"
    mkdir -p "${HOME}/.postgresql"
}

#######################################
# Остановить текущие контейнеры.
# Внимание: флаг -v не используется намеренно - он удаляет именованные тома
# (postgres-data, minio-data). Сертификаты Let's Encrypt хранятся
# в bind-mount ./traefik/letsencrypt и командой down не затрагиваются.
#######################################
function compose_down() {
    $COMPOSE_CMD down
}

#######################################
# Вытянуть свежие образы из реестра.
#######################################
function compose_pull() {
    $COMPOSE_CMD pull
}

#######################################
# Запустить контейнеры в фоновом режиме.
#######################################
function compose_up() {
    $COMPOSE_CMD up -d
    $COMPOSE_CMD ps
}

#######################################
# Последовательный вызов основных функций скрипта.
#######################################
function main() {
    load_dotenv
    load_postgres_cert
    pull_repository
    create_docker_directories
    compose_down
    compose_pull
    compose_up
}

main
